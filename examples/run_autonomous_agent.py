"""
Autonomous Agent Demo — Multi-Skill Parallel Pipeline
======================================================

Demonstrates the PipelineOrchestrator executing the workflow defined in
  workflows/Autonomous Agent Workflow.json

Pipeline structure (from the workflow JSON):

  [document_intake]          ← Wave 1  (sequential start)
         │
  [borrower_profile]         ← Wave 2  (sequential)
       ╱     ╲
[credit_memo] [collateral_assessment]  ← Wave 3  (PARALLEL)
       ╲     ╱
  [credit_decision]          ← Wave 4  (sequential end)

Run:
    cd c:/My AI Projects/CreditMemoGenerationFramework
    python examples/run_autonomous_agent.py
"""

import os
import sys
from pathlib import Path

# Allow running from any directory
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from skill_engine import PipelineOrchestrator

load_dotenv()

console = Console()


def main():
    # ── 1. Create the orchestrator ────────────────────────────────────────────
    orchestrator = PipelineOrchestrator(
        skills_dir=str(ROOT / "skills"),
        base_path=str(ROOT),

        # Choose your LLM provider:

        # Option A — Anthropic Claude (recommended)
        llm_provider="anthropic",
        model_name="claude-sonnet-4-6",
        api_key=os.getenv("ANTHROPIC_API_KEY"),

        # Option B — OpenAI
        # llm_provider="openai",
        # model_name="gpt-4o",
        # api_key=os.getenv("OPENAI_API_KEY"),

        max_workers=4,   # up to 4 parallel threads (covers the 2 parallel skills)
        verbose=True,
    )

    # ── 2. Run the workflow ───────────────────────────────────────────────────
    console.print(Panel.fit(
        "[bold cyan]Autonomous Credit Evaluation Agent[/bold cyan]\n"
        "[dim]5-skill pipeline with parallel processing[/dim]",
        border_style="cyan",
    ))

    result = orchestrator.execute_workflow_file(
        workflow_path=str(ROOT / "workflows" / "Autonomous Agent Workflow.json"),
        initial_variables={
            # Seed variables visible to all skills via pipeline luggage.
            # Skills can reference these in their steps.
            "applicant_name": "ACME Manufacturing Corporation",
            "loan_amount_requested": 500000,
            "loan_purpose": "Equipment expansion and working capital",
        },
    )

    # ── 3. Print execution summary ────────────────────────────────────────────
    console.print()
    console.rule("[bold]Pipeline Result[/bold]")

    # Execution waves — shows which skills ran in parallel
    wave_table = Table(show_header=True, header_style="bold magenta", title="Execution Waves")
    wave_table.add_column("Wave", style="bold", justify="center")
    wave_table.add_column("Skills Executed", style="cyan")
    wave_table.add_column("Mode", style="bold")

    for i, wave in enumerate(result.execution_order, 1):
        skill_names = "\n".join(wave)
        mode = "[bold yellow]PARALLEL[/bold yellow]" if len(wave) > 1 else "[white]sequential[/white]"
        wave_table.add_row(str(i), skill_names, mode)

    console.print(wave_table)
    console.print()

    # Per-node step output counts
    output_table = Table(show_header=True, header_style="bold magenta", title="Node Outputs")
    output_table.add_column("Node ID", style="dim")
    output_table.add_column("Steps Completed", justify="right")
    output_table.add_column("Variables Extracted", justify="right")

    for node_id, luggage in result.node_luggages.items():
        short_id = node_id.split("-")[0]   # e.g. "document_intake"
        output_table.add_row(
            short_id,
            str(len(luggage.step_outputs)),
            str(len(luggage.variables)),
        )

    console.print(output_table)
    console.print()

    # Final pipeline summary
    console.print(Panel(
        result.summary(),
        title="[bold green]Summary[/bold green]",
        border_style="green",
    ))

    # ── 4. Show the final credit decision output ──────────────────────────────
    final_luggage = result.final_luggage
    last_step = list(final_luggage.step_outputs.keys())[-1] if final_luggage.step_outputs else None

    if last_step:
        console.print()
        console.rule("[bold]Final Output[/bold]")
        console.print(f"[dim]From step: {last_step}[/dim]\n")
        console.print(final_luggage.step_outputs[last_step])


if __name__ == "__main__":
    main()
