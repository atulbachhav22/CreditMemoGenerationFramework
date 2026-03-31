"""
PipelineOrchestrator - Executes multi-skill workflows defined as DAGs.

Reads a workflow JSON (nodes + edges), resolves execution order via
topological dependency tracking, and runs independent nodes concurrently
using a thread pool. Sequential nodes wait for all predecessors to finish
before starting.

Thread-safety model:
  - Each node gets its own SkillProcessor instance (avoids shared mutable
    state in LLMOrchestrator.conversation_history).
  - Pipeline luggage merging is protected by a threading.Lock.
  - Node luggages are written once per node and read-only afterward.
"""

import json
import threading
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from skill_engine.models.workflow import WorkflowDefinition, WorkflowNode
from skill_engine.models.luggage import SkillLuggage
from skill_engine.processor.skill_processor import SkillProcessor


class PipelineResult:
    """
    Holds the complete output of a pipeline execution.

    Attributes:
        workflow_name:    Name of the executed workflow
        final_luggage:    Merged luggage from all completed nodes
        node_luggages:    Per-node luggage keyed by node ID
        node_errors:      Exceptions from failed nodes, keyed by node ID
        duration_seconds: Wall-clock execution time
        completed_nodes:  IDs of nodes that finished (success or failure)
    """

    def __init__(
        self,
        workflow_name: str,
        final_luggage: SkillLuggage,
        node_luggages: Dict[str, SkillLuggage],
        node_errors: Dict[str, Exception],
        duration_seconds: float,
        completed_nodes: List[str],
        execution_order: List[List[str]],
    ):
        self.workflow_name = workflow_name
        self.final_luggage = final_luggage
        self.node_luggages = node_luggages
        self.node_errors = node_errors
        self.duration_seconds = duration_seconds
        self.completed_nodes = completed_nodes
        self.execution_order = execution_order  # list of waves [[node_id, ...], ...]

    @property
    def success(self) -> bool:
        return len(self.node_errors) == 0

    def get_node_luggage(self, node_id: str) -> Optional[SkillLuggage]:
        """Get the luggage produced by a specific node."""
        return self.node_luggages.get(node_id)

    def summary(self) -> str:
        lines = [
            f"Pipeline : {self.workflow_name}",
            f"Status   : {'SUCCESS' if self.success else 'FAILED'}",
            f"Duration : {self.duration_seconds:.1f}s",
            f"Nodes    : {len(self.completed_nodes)} completed",
        ]
        if self.node_errors:
            lines.append(f"Errors   : {list(self.node_errors.keys())}")
        lines.append("Waves    :")
        for i, wave in enumerate(self.execution_order, 1):
            lines.append(f"  Wave {i}: {', '.join(wave)}")
        return "\n".join(lines)


class PipelineOrchestrator:
    """
    Executes a workflow JSON as a parallel-aware skill pipeline.

    Usage::

        orchestrator = PipelineOrchestrator(
            skills_dir="skills",
            llm_provider="anthropic",
            model_name="claude-sonnet-4-6",
        )
        result = orchestrator.execute_workflow_file("workflows/Autonomous Agent Workflow.json")
        print(result.summary())
    """

    def __init__(
        self,
        skills_dir: str = "skills",
        llm_provider: str = "openai",
        model_name: str = "gpt-4",
        temperature: float = 0.0,
        api_key: Optional[str] = None,
        base_path: Optional[str] = None,
        max_workers: int = 4,
        verbose: bool = True,
        reference_files: Optional[List[str]] = None,
        **llm_kwargs,
    ):
        """
        Args:
            skills_dir:      Directory containing skill .md files (relative or absolute)
            llm_provider:    LLM provider — "openai" or "anthropic"
            model_name:      Model name passed to SkillProcessor
            temperature:     Sampling temperature
            api_key:         API key (falls back to env vars if None)
            base_path:       Root path for resolving relative file refs in skills
            max_workers:     Maximum parallel threads in the thread pool
            verbose:         Enable rich console output
            reference_files: Optional list of file paths injected as global reference
                             files into every skill node (e.g. uploaded documents)
            **llm_kwargs:    Extra kwargs forwarded to SkillProcessor / LLMOrchestrator
        """
        self.skills_dir = Path(skills_dir)
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key
        self.llm_kwargs = llm_kwargs
        self.max_workers = max_workers
        self.verbose = verbose
        self.reference_files: List[str] = reference_files or []
        self.console = Console() if verbose else None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute_workflow_file(
        self,
        workflow_path: str,
        initial_variables: Optional[Dict[str, Any]] = None,
    ) -> PipelineResult:
        """
        Load a workflow JSON file and execute it.

        Args:
            workflow_path:      Path to the workflow .json file
            initial_variables:  Optional seed variables injected into every node

        Returns:
            PipelineResult with all outputs and metadata
        """
        path = Path(workflow_path)
        if not path.exists():
            raise FileNotFoundError(f"Workflow file not found: {path}")

        if self.verbose:
            self.console.print(f"\n[bold blue]Loading workflow:[/bold blue] {path.name}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        workflow = WorkflowDefinition(**data)
        return self.execute_workflow(workflow, initial_variables)

    def execute_workflow(
        self,
        workflow: WorkflowDefinition,
        initial_variables: Optional[Dict[str, Any]] = None,
    ) -> PipelineResult:
        """
        Execute a WorkflowDefinition object.

        Algorithm:
          1. Build predecessor / successor maps from edges.
          2. Seed the ready-queue with nodes that have no predecessors.
          3. Submit all ready nodes to the thread pool simultaneously.
          4. As each node completes, unlock successors whose predecessors
             are all done and add them to the ready queue.
          5. Repeat until the thread pool is idle and the ready queue is empty.

        Args:
            workflow:           WorkflowDefinition to execute
            initial_variables:  Optional seed variables

        Returns:
            PipelineResult
        """
        started_at = datetime.now()

        if self.verbose:
            self.console.rule(f"[bold green]Pipeline: {workflow.name}[/bold green]")
            self.console.print(f"[dim]{len(workflow.nodes)} nodes | {len(workflow.edges)} edges[/dim]\n")

        # ── Build DAG lookup structures ───────────────────────────────────────
        node_map: Dict[str, WorkflowNode] = {n.id: n for n in workflow.nodes}

        # predecessors[node_id] = set of node_ids that must finish first
        predecessors: Dict[str, Set[str]] = {n.id: set(workflow.predecessors(n.id)) for n in workflow.nodes}
        # successors[node_id] = list of node_ids unlocked when this one finishes
        successors: Dict[str, List[str]] = {n.id: workflow.successors(n.id) for n in workflow.nodes}

        if self.verbose:
            self._print_execution_plan(workflow, node_map, predecessors, successors)

        # ── Shared pipeline state (lock-protected) ────────────────────────────
        completed: Set[str] = set()
        node_luggages: Dict[str, SkillLuggage] = {}
        node_errors: Dict[str, Exception] = {}
        execution_waves: List[List[str]] = []   # for the result summary
        lock = threading.Lock()

        # Seed luggage carries initial_variables into all start nodes
        seed_luggage = SkillLuggage(skill_name=workflow.name)
        if initial_variables:
            for k, v in initial_variables.items():
                seed_luggage.set_variable(k, v)

        # ── Execution loop ────────────────────────────────────────────────────
        ready: List[str] = workflow.start_nodes()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # pending maps Future → node_id
            pending: Dict[concurrent.futures.Future, str] = {}

            while ready or pending:

                # Submit every node in the current ready batch
                if ready:
                    wave_labels = [node_map[nid].label for nid in ready]
                    execution_waves.append(ready[:])

                    if self.verbose:
                        if len(ready) > 1:
                            self.console.print(
                                f"[bold yellow]⟳ Parallel wave:[/bold yellow] "
                                + " | ".join(f"[cyan]{l}[/cyan]" for l in wave_labels)
                            )
                        else:
                            self.console.print(f"[bold]→ Running:[/bold] [cyan]{wave_labels[0]}[/cyan]")

                for node_id in ready:
                    node = node_map[node_id]
                    merged_luggage = self._merge_luggages(
                        predecessor_ids=predecessors[node_id],
                        node_luggages=node_luggages,
                        seed_luggage=seed_luggage,
                    )
                    future = executor.submit(self._execute_node, node, merged_luggage)
                    pending[future] = node_id

                ready = []

                # Block until at least one node finishes
                done_futures, _ = wait(pending.keys(), return_when=FIRST_COMPLETED)

                for future in done_futures:
                    node_id = pending.pop(future)
                    node = node_map[node_id]

                    try:
                        result_luggage = future.result()

                        with lock:
                            node_luggages[node_id] = result_luggage
                            completed.add(node_id)

                        if self.verbose:
                            self.console.print(f"  [green]✓[/green] {node.label}")

                        # Unlock successors whose all predecessors are now done
                        with lock:
                            for succ_id in successors[node_id]:
                                if predecessors[succ_id].issubset(completed):
                                    ready.append(succ_id)

                    except Exception as exc:
                        with lock:
                            node_errors[node_id] = exc
                            completed.add(node_id)

                        logger.error(f"Node '{node.label}' failed: {exc}")
                        if self.verbose:
                            self.console.print(f"  [red]✗[/red] {node.label} — {exc}")

                        # Re-raise to abort the entire pipeline on first failure.
                        # Cancel remaining pending futures before raising.
                        for f in pending:
                            f.cancel()
                        raise RuntimeError(
                            f"Pipeline aborted: node '{node.label}' failed.\n"
                            f"Cause: {exc}"
                        ) from exc

        # ── Build final merged luggage ────────────────────────────────────────
        final_luggage = self._merge_luggages(
            predecessor_ids=set(node_luggages.keys()),
            node_luggages=node_luggages,
            seed_luggage=seed_luggage,
        )
        final_luggage.execution_metadata["completed"] = True
        final_luggage.execution_metadata["workflow"] = workflow.name
        final_luggage.execution_metadata["nodes_completed"] = len(completed)

        duration = (datetime.now() - started_at).total_seconds()

        if self.verbose:
            self.console.rule("[bold green]Pipeline Complete[/bold green]")
            self.console.print(
                f"[dim]Duration: {duration:.1f}s | "
                f"Nodes: {len(completed)} | "
                f"Parallel waves: {len([w for w in execution_waves if len(w) > 1])}[/dim]\n"
            )

        return PipelineResult(
            workflow_name=workflow.name,
            final_luggage=final_luggage,
            node_luggages=node_luggages,
            node_errors=node_errors,
            duration_seconds=duration,
            completed_nodes=list(completed),
            execution_order=execution_waves,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _execute_node(self, node: WorkflowNode, luggage: SkillLuggage) -> SkillLuggage:
        """
        Execute one skill node in its own thread.

        A fresh SkillProcessor is created per node to avoid shared mutable
        state (LLMOrchestrator.conversation_history) across parallel threads.

        The merged upstream luggage is passed as initial_variables so the
        skill can see all prior step outputs and extracted variables.
        """
        skill_file = self.skills_dir / f"{node.skill_name}.md"
        if not skill_file.exists():
            raise FileNotFoundError(
                f"Skill file not found: {skill_file}  "
                f"(node: '{node.label}', skill_name: '{node.skill_name}')"
            )

        logger.info(f"[{node.skill_name}] thread starting")

        # Each thread gets its own processor — no shared mutable state
        processor = SkillProcessor(
            llm_provider=self.llm_provider,
            model_name=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key,
            base_path=str(self.base_path),
            verbose=self.verbose,
            **self.llm_kwargs,
        )

        # Parse skill so we can inject reference files before executing
        skill = processor.parser.parse_file(str(skill_file))
        if self.reference_files:
            skill.global_reference_files.extend(self.reference_files)

        result_luggage = processor.execute_skill(
            skill,
            initial_variables=luggage.variables.copy(),
        )

        # Propagate upstream step_outputs into the result so downstream nodes
        # can see the full pipeline history, not just this skill's steps.
        for step_name, output in luggage.step_outputs.items():
            if step_name not in result_luggage.step_outputs:
                result_luggage.step_outputs[step_name] = output

        # Propagate loaded files cache to avoid re-reading shared files
        for file_path, content in luggage.loaded_files.items():
            if file_path not in result_luggage.loaded_files:
                result_luggage.loaded_files[file_path] = content

        logger.info(f"[{node.skill_name}] thread finished")
        return result_luggage

    def _merge_luggages(
        self,
        predecessor_ids: Set[str],
        node_luggages: Dict[str, SkillLuggage],
        seed_luggage: SkillLuggage,
    ) -> SkillLuggage:
        """
        Produce a new SkillLuggage that combines the seed luggage with the
        outputs from all specified predecessor nodes.

        Merge order: seed → predecessors (in insertion order).
        Later entries overwrite earlier ones on key conflicts, so the most
        recently completed predecessor's data takes precedence.
        """
        merged = SkillLuggage(skill_name="pipeline_context")

        # Layer 1: seed (initial_variables and any global context)
        merged.variables.update(seed_luggage.variables)
        merged.step_outputs.update(seed_luggage.step_outputs)
        merged.loaded_files.update(seed_luggage.loaded_files)
        merged.api_responses.update(seed_luggage.api_responses)

        # Layer 2: each predecessor's outputs
        for pred_id in predecessor_ids:
            pred = node_luggages.get(pred_id)
            if pred is None:
                continue
            merged.variables.update(pred.variables)
            merged.step_outputs.update(pred.step_outputs)
            merged.loaded_files.update(pred.loaded_files)
            merged.api_responses.update(pred.api_responses)
            merged.verification_results.update(pred.verification_results)

        return merged

    def _print_execution_plan(
        self,
        workflow: WorkflowDefinition,
        node_map: Dict[str, WorkflowNode],
        predecessors: Dict[str, Set[str]],
        successors: Dict[str, List[str]],
    ) -> None:
        """Render a rich table showing the DAG execution plan."""
        table = Table(
            title=f"Execution Plan — {workflow.name}",
            show_header=True,
            header_style="bold magenta",
            show_lines=True,
        )
        table.add_column("Node", style="cyan", no_wrap=True)
        table.add_column("Waits For", style="yellow")
        table.add_column("Unlocks", style="green")
        table.add_column("Execution", style="bold")

        # Build edge-type lookup: (source_id, target_id) → edge_type
        edge_type_map = {(e.source, e.target): e.edge_type for e in workflow.edges}

        for node in workflow.nodes:
            preds = predecessors[node.id]
            succs = successors[node.id]

            waits_for = "\n".join(node_map[p].label for p in preds) if preds else "— (start)"
            unlocks = "\n".join(node_map[s].label for s in succs) if succs else "— (end)"

            # Determine how this node is triggered
            incoming_types = {edge_type_map.get((p, node.id), "sequential") for p in preds}
            if not preds:
                exec_mode = "[bold green]START[/bold green]"
            elif "parallel" in incoming_types:
                exec_mode = "[bold yellow]PARALLEL[/bold yellow]"
            else:
                exec_mode = "[white]sequential[/white]"

            table.add_row(node.label, waits_for, unlocks, exec_mode)

        self.console.print(table)
        self.console.print()
