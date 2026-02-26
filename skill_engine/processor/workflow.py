"""
Workflow engine for composing and executing multiple skills.

Supports:
- Sequential skill execution
- Parallel skill execution
- Skill dependency chains
- Result aggregation
"""

from typing import Optional, Dict, Any, List, Callable
from pathlib import Path
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from skill_engine.models.skill import Skill
from skill_engine.models.luggage import SkillLuggage
from skill_engine.processor.skill_processor import SkillProcessor


@dataclass
class SkillTask:
    """Represents a skill to be executed in a workflow."""
    
    name: str
    skill_path: str
    processor: SkillProcessor
    initial_variables: Optional[Dict[str, Any]] = None
    dependencies: List[str] = field(default_factory=list)
    
    def execute(self, context: Dict[str, SkillLuggage]) -> SkillLuggage:
        """
        Execute this skill task.
        
        Args:
            context: Dictionary of completed skill results
            
        Returns:
            SkillLuggage from execution
        """
        # Start with initial variables
        variables = self.initial_variables.copy() if self.initial_variables else {}
        
        # Add outputs from dependent skills
        for dep_name in self.dependencies:
            if dep_name in context:
                dep_luggage = context[dep_name]
                
                # Pass the final step output from dependency
                # step_outputs is a dict, so get the last value
                if dep_luggage.step_outputs:
                    # Convert dict values to list and get the last one
                    step_outputs_list = list(dep_luggage.step_outputs.values())
                    last_step_output = step_outputs_list[-1]
                    
                    # Store as both the dependency name and as structured key
                    variables[f"{dep_name}_output"] = last_step_output
                    variables[dep_name] = last_step_output
                
                # Also merge any extracted variables from dependency
                if dep_luggage.variables:
                    variables.update(dep_luggage.variables)
        
        logger.info(f"Executing skill task: {self.name} with dependencies: {self.dependencies}")
        if self.dependencies:
            logger.info(f"Passing context variables: {list(variables.keys())}")
        
        return self.processor.execute_skill_file(
            self.skill_path,
            initial_variables=variables
        )


class WorkflowBuilder:
    """Builder for creating skill workflows."""
    
    def __init__(self, verbose: bool = True):
        """Initialize workflow builder."""
        self.tasks: Dict[str, SkillTask] = {}
        self.verbose = verbose
        self.console = Console() if verbose else None
        self.execution_order: List[str] = []
    
    def add_skill(
        self,
        name: str,
        skill_path: str,
        processor: SkillProcessor,
        initial_variables: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None
    ) -> 'WorkflowBuilder':
        """
        Add a skill to the workflow.
        
        Args:
            name: Unique name for this skill in the workflow
            skill_path: Path to the skill markdown file
            processor: SkillProcessor instance
            initial_variables: Variables to pass to the skill
            dependencies: List of skill names this depends on
            
        Returns:
            Self for chaining
        """
        if name in self.tasks:
            raise ValueError(f"Skill '{name}' already exists in workflow")
        
        self.tasks[name] = SkillTask(
            name=name,
            skill_path=skill_path,
            processor=processor,
            initial_variables=initial_variables,
            dependencies=dependencies or []
        )
        
        if self.verbose:
            self.console.print(f"[dim]Added skill: {name}[/dim]")
        
        return self
    
    def validate_dependencies(self) -> bool:
        """
        Validate that all dependencies are satisfied.
        
        Returns:
            True if valid, raises ValueError if invalid
        """
        defined_skills = set(self.tasks.keys())
        
        for name, task in self.tasks.items():
            for dep in task.dependencies:
                if dep not in defined_skills:
                    raise ValueError(
                        f"Skill '{name}' depends on '{dep}' which is not defined"
                    )
        
        return True
    
    def _topological_sort(self) -> List[str]:
        """
        Topological sort for sequential execution.
        
        Returns:
            Ordered list of skill names
        """
        visited = set()
        order = []
        
        def visit(name: str):
            if name in visited:
                return
            visited.add(name)
            
            task = self.tasks[name]
            for dep in task.dependencies:
                visit(dep)
            
            order.append(name)
        
        for name in self.tasks:
            visit(name)
        
        return order
    
    def build_sequential(self) -> 'SequentialWorkflow':
        """Build a sequential workflow."""
        self.validate_dependencies()
        execution_order = self._topological_sort()
        return SequentialWorkflow(self.tasks, execution_order, self.verbose)
    
    def build_parallel(self, max_workers: Optional[int] = None) -> 'ParallelWorkflow':
        """
        Build a parallel workflow with dependency constraints.
        
        Args:
            max_workers: Maximum number of concurrent workers (None = cpu_count)
            
        Returns:
            ParallelWorkflow instance
        """
        self.validate_dependencies()
        return ParallelWorkflow(self.tasks, self.verbose, max_workers=max_workers)


class SequentialWorkflow:
    """Executes skills sequentially in dependency order."""
    
    def __init__(
        self,
        tasks: Dict[str, SkillTask],
        execution_order: List[str],
        verbose: bool = True
    ):
        """
        Initialize sequential workflow.
        
        Args:
            tasks: Dictionary of skill tasks
            execution_order: Order to execute skills
            verbose: Enable verbose output
        """
        self.tasks = tasks
        self.execution_order = execution_order
        self.verbose = verbose
        self.console = Console() if verbose else None
        self.results: Dict[str, SkillLuggage] = {}
    
    def execute(self) -> Dict[str, SkillLuggage]:
        """
        Execute all skills sequentially.
        
        Returns:
            Dictionary mapping skill names to SkillLuggage results
        """
        if self.verbose:
            self.console.print("\n[bold green]Executing Sequential Workflow[/bold green]")
            self.console.print(f"[dim]Order: {' → '.join(self.execution_order)}[/dim]\n")
        
        self.results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console if self.verbose else None,
            disable=not self.verbose
        ) as progress:
            for i, skill_name in enumerate(self.execution_order, 1):
                task = self.tasks[skill_name]
                
                task_id = progress.add_task(
                    f"[cyan]({i}/{len(self.execution_order)})[/cyan] {skill_name}...",
                    total=None
                )
                
                try:
                    luggage = task.execute(self.results)
                    self.results[skill_name] = luggage
                    progress.update(task_id, completed=True, visible=False)
                    
                    if self.verbose:
                        self.console.print(f"[green]✓[/green] {skill_name} completed")
                
                except Exception as e:
                    if self.verbose:
                        self.console.print(f"[red]✗[/red] {skill_name} failed: {e}")
                    raise
        
        if self.verbose:
            self.console.print(
                f"\n[bold green]✓ Sequential workflow complete![/bold green]\n"
            )
        
        return self.results
    
    def get_result(self, skill_name: str) -> Optional[SkillLuggage]:
        """Get result from a specific skill."""
        return self.results.get(skill_name)
    
    def get_all_results(self) -> Dict[str, SkillLuggage]:
        """Get all results."""
        return self.results


class ParallelWorkflow:
    """Executes skills in parallel respecting dependencies."""
    
    def __init__(
        self,
        tasks: Dict[str, SkillTask],
        verbose: bool = True,
        max_workers: Optional[int] = None
    ):
        """
        Initialize parallel workflow.
        
        Args:
            tasks: Dictionary of skill tasks
            verbose: Enable verbose output
            max_workers: Maximum parallel workers (None = cpu_count)
        """
        self.tasks = tasks
        self.verbose = verbose
        self.console = Console() if verbose else None
        self.max_workers = max_workers
        self.results: Dict[str, SkillLuggage] = {}
        self._executed = set()
    
    def _get_ready_tasks(self) -> List[str]:
        """Get tasks ready to execute (dependencies satisfied)."""
        ready = []
        
        for name, task in self.tasks.items():
            if name in self._executed:
                continue
            
            # Check if all dependencies are done
            deps_satisfied = all(dep in self._executed for dep in task.dependencies)
            
            if deps_satisfied:
                ready.append(name)
        
        return ready
    
    def execute(self) -> Dict[str, SkillLuggage]:
        """
        Execute skills in parallel respecting dependencies.
        
        Returns:
            Dictionary mapping skill names to SkillLuggage results
        """
        if self.verbose:
            self.console.print("\n[bold green]Executing Parallel Workflow[/bold green]\n")
        
        self.results = {}
        self._executed = set()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            
            while len(self._executed) < len(self.tasks):
                ready_tasks = self._get_ready_tasks()
                
                if not ready_tasks:
                    if self._executed:
                        # Deadlock - circular dependency
                        raise ValueError(
                            f"Circular dependency detected. "
                            f"Executed: {self._executed}, "
                            f"Remaining: {set(self.tasks.keys()) - self._executed}"
                        )
                    else:
                        raise ValueError("No tasks ready to execute")
                
                # Submit ready tasks
                for skill_name in ready_tasks:
                    task = self.tasks[skill_name]
                    future = executor.submit(task.execute, self.results)
                    futures[future] = skill_name
                    
                    if self.verbose:
                        self.console.print(f"[dim]Starting: {skill_name}[/dim]")
                
                # Wait for at least one to complete
                if futures:
                    for future in as_completed(futures):
                        skill_name = futures.pop(future)
                        
                        try:
                            luggage = future.result()
                            self.results[skill_name] = luggage
                            self._executed.add(skill_name)
                            
                            if self.verbose:
                                self.console.print(
                                    f"[green]✓[/green] {skill_name} completed"
                                )
                        
                        except Exception as e:
                            if self.verbose:
                                self.console.print(
                                    f"[red]✗[/red] {skill_name} failed: {e}"
                                )
                            raise
        
        if self.verbose:
            self.console.print(
                f"\n[bold green]✓ Parallel workflow complete![/bold green]\n"
            )
        
        return self.results
    
    def get_result(self, skill_name: str) -> Optional[SkillLuggage]:
        """Get result from a specific skill."""
        return self.results.get(skill_name)
    
    def get_all_results(self) -> Dict[str, SkillLuggage]:
        """Get all results."""
        return self.results