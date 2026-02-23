"""
SkillProcessor - Core orchestration engine for executing Skills.

This is the main class that coordinates:
- Skill parsing
- Step-by-step execution
- State management via SkillLuggage
- Verification loops
- File loading
- LLM orchestration
"""

from typing import Optional, Dict, Any
from pathlib import Path
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from skill_engine.models.skill import Skill, SkillStep
from skill_engine.models.luggage import SkillLuggage
from skill_engine.parser.markdown_parser import SkillMarkdownParser
from skill_engine.llm.orchestrator import LLMOrchestrator
from skill_engine.utils.file_loader import FileLoader
from skill_engine.utils.api_caller import ApiCaller, ApiCallError


class SkillProcessor:
    """
    Core processor for executing Skills defined in Markdown files.

    This class orchestrates the entire skill execution workflow:
    1. Parse skill from Markdown
    2. Initialize luggage (state)
    3. Execute steps sequentially
    4. Load reference files as needed
    5. Verify outputs against criteria
    6. Manage state between steps
    7. Return final output

    The processor is skill-agnostic and can execute any properly formatted
    skill definition.
    """

    def __init__(
        self,
        llm_provider: str = "openai",
        model_name: str = "gpt-4",
        temperature: float = 0.0,
        api_key: Optional[str] = None,
        base_path: Optional[str] = None,
        verbose: bool = True,
        **llm_kwargs
    ):
        """
        Initialize the SkillProcessor.

        Args:
            llm_provider: LLM provider ("openai", "anthropic")
            model_name: Model name
            temperature: Sampling temperature
            api_key: API key (optional)
            base_path: Base path for resolving relative file paths
            verbose: Enable rich console output
            **llm_kwargs: Additional LLM parameters
        """
        self.parser = SkillMarkdownParser()
        self.orchestrator = LLMOrchestrator(
            llm_provider=llm_provider,
            model_name=model_name,
            temperature=temperature,
            api_key=api_key,
            **llm_kwargs
        )
        self.file_loader = FileLoader()
        self.api_caller = ApiCaller()

        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.verbose = verbose
        self.console = Console() if verbose else None

        logger.info("SkillProcessor initialized")

    def execute_skill_file(
        self,
        skill_file_path: str,
        initial_variables: Optional[Dict[str, Any]] = None
    ) -> SkillLuggage:
        """
        Execute a skill from a Markdown file.

        Args:
            skill_file_path: Path to the .md skill file
            initial_variables: Initial variables to set in luggage

        Returns:
            SkillLuggage containing all outputs and state
        """
        # Parse skill
        if self.verbose:
            self.console.print(f"[bold blue]Loading skill from:[/bold blue] {skill_file_path}")

        skill = self.parser.parse_file(skill_file_path)

        # Execute skill
        return self.execute_skill(skill, initial_variables)

    def execute_skill(
        self,
        skill: Skill,
        initial_variables: Optional[Dict[str, Any]] = None
    ) -> SkillLuggage:
        """
        Execute a parsed Skill object.

        Args:
            skill: Parsed Skill object
            initial_variables: Initial variables to set in luggage

        Returns:
            SkillLuggage containing all outputs and state
        """
        # Initialize luggage
        luggage = SkillLuggage(skill_name=skill.metadata.name)

        if initial_variables:
            for key, value in initial_variables.items():
                luggage.set_variable(key, value)

        # Load global reference files
        if skill.global_reference_files:
            self._load_reference_files(skill.global_reference_files, luggage)

        # Fetch global API context
        if skill.global_api_context:
            self._fetch_api_context(skill.global_api_context, luggage, scope="global")

        # Display skill info
        if self.verbose:
            self.console.print(f"\n[bold green]Executing Skill:[/bold green] {skill.metadata.name}")
            self.console.print(f"[dim]Version: {skill.metadata.version}[/dim]")
            self.console.print(f"[dim]Steps: {skill.get_total_steps()}[/dim]\n")

        # Execute steps sequentially
        for step in skill.steps:
            luggage.current_step = step.name
            self._execute_step(step, skill, luggage)

        # Mark completion
        luggage.execution_metadata["completed"] = True
        luggage.execution_metadata["model_used"] = self.orchestrator.model_name

        if self.verbose:
            self.console.print("\n[bold green]✓ Skill execution complete![/bold green]\n")

        return luggage

    def _execute_step(
        self,
        step: SkillStep,
        skill: Skill,
        luggage: SkillLuggage
    ) -> None:
        """
        Execute a single skill step.

        Args:
            step: SkillStep to execute
            skill: Parent Skill object
            luggage: SkillLuggage for state management
        """
        if self.verbose:
            self.console.print(f"[bold cyan]Step {step.step_number}:[/bold cyan] {step.name}")

        # Load step-specific reference files
        step_ref_files_content = {}
        if step.reference_files:
            step_ref_files_content = self._load_reference_files(
                step.reference_files,
                luggage,
                return_dict=True
            )

        # Fetch step-level API context
        if step.api_context:
            self._fetch_api_context(step.api_context, luggage, scope=f"step_{step.step_number}")

        # Build context for LLM
        luggage_context = luggage.get_context_summary()

        # Execute LLM call
        max_retries = 3
        if step.verification:
            max_retries = step.verification.max_retries

        for attempt in range(max_retries):
            try:
                # Call LLM
                output = self.orchestrator.execute_step(
                    instruction=step.instruction,
                    context=skill.context,
                    reference_files_content=step_ref_files_content,
                    luggage_context=luggage_context,
                    expected_format=step.expected_output_format,
                    api_context_data=luggage.api_responses if luggage.api_responses else None
                )

                # Verify output if criteria specified
                if step.verification:
                    passed, explanation = self._verify_step_output(
                        output, step.verification, step.name
                    )

                    luggage.record_verification(step.name, passed)

                    if not passed:
                        if self.verbose:
                            self.console.print(f"[yellow]  ⚠ Verification failed (attempt {attempt + 1}/{max_retries})[/yellow]")
                            self.console.print(f"[dim]  {explanation}[/dim]")

                        if attempt < max_retries - 1:
                            # Retry with feedback
                            continue
                        else:
                            # Max retries reached
                            if step.verification.fail_action == "halt":
                                raise ValueError(f"Step verification failed after {max_retries} attempts: {explanation}")
                            elif step.verification.fail_action == "skip":
                                logger.warning(f"Skipping step {step.name} after verification failure")
                                return
                            # Otherwise, continue with the output despite failure
                    else:
                        if self.verbose:
                            self.console.print(f"[green]  ✓ Verification passed[/green]")

                # Store output
                luggage.add_step_output(step.name, output)

                # Extract variables if specified
                if step.variables_to_extract:
                    self._extract_variables(output, step.variables_to_extract, luggage)

                # Success - break retry loop
                break

            except Exception as e:
                logger.error(f"Step {step.name} execution failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise

        if self.verbose:
            output_preview = output[:200] + "..." if len(output) > 200 else output
            self.console.print(f"[dim]  Output: {output_preview}[/dim]\n")

    def _load_reference_files(
        self,
        file_paths: list[str],
        luggage: SkillLuggage,
        return_dict: bool = False
    ) -> Optional[Dict[str, str]]:
        """
        Load reference files into luggage.

        Args:
            file_paths: List of file paths to load
            luggage: SkillLuggage to store content
            return_dict: If True, return dict of file contents

        Returns:
            Optional dictionary of file paths to contents
        """
        file_contents = {}

        for file_path in file_paths:
            # Resolve relative paths
            resolved_path = self._resolve_file_path(file_path)

            # Check if already loaded
            existing_content = luggage.get_file_content(str(resolved_path))
            if existing_content:
                file_contents[file_path] = existing_content
                continue

            # Load file
            try:
                content = self.file_loader.load_file(str(resolved_path))
                luggage.load_file_content(str(resolved_path), content)
                file_contents[file_path] = content

                if self.verbose:
                    self.console.print(f"[dim]  Loaded: {file_path}[/dim]")

            except Exception as e:
                logger.error(f"Failed to load file {file_path}: {str(e)}")
                raise

        return file_contents if return_dict else None

    def _fetch_api_context(
        self,
        api_definitions: list,
        luggage: SkillLuggage,
        scope: str = "global"
    ) -> None:
        """
        Fetch API context data and store in luggage.

        Args:
            api_definitions: List of ApiContextDefinition objects
            luggage: SkillLuggage to store responses
            scope: Scope identifier for logging (e.g., "global", "step_1")
        """
        for api_def in api_definitions:
            # Check if already fetched (avoid duplicate calls)
            existing = luggage.get_api_response(api_def.alias)
            if existing is not None:
                logger.info(f"API context '{api_def.alias}' already loaded, skipping")
                continue

            try:
                data = self.api_caller.call_api(api_def)
                luggage.store_api_response(api_def.alias, data)

                if self.verbose:
                    data_preview = str(data)[:100]
                    if len(str(data)) > 100:
                        data_preview += "..."
                    self.console.print(f"[dim]  API [{api_def.alias}]: {data_preview}[/dim]")

            except ApiCallError as e:
                logger.error(f"API context fetch failed ({scope}): {e}")
                # Store error marker so the LLM knows the data is unavailable
                luggage.store_api_response(
                    api_def.alias,
                    {"_error": str(e), "_alias": api_def.alias}
                )
                if self.verbose:
                    self.console.print(
                        f"[yellow]  Warning: API call '{api_def.alias}' failed: {e}[/yellow]"
                    )

    def _resolve_file_path(self, file_path: str) -> Path:
        """
        Resolve a file path relative to base_path.

        Args:
            file_path: File path (may be relative or absolute)

        Returns:
            Resolved Path object
        """
        path = Path(file_path)
        if path.is_absolute():
            return path
        else:
            return self.base_path / path

    def _verify_step_output(
        self,
        output: str,
        verification: Any,
        step_name: str
    ) -> tuple[bool, str]:
        """
        Verify step output against verification criteria.

        Args:
            output: Step output to verify
            verification: VerificationCriteria object
            step_name: Name of the step

        Returns:
            Tuple of (passed: bool, explanation: str)
        """
        return self.orchestrator.verify_output(
            output=output,
            verification_rules=verification.rules,
            required_elements=verification.required_elements
        )

    def _extract_variables(
        self,
        output: str,
        variable_names: list[str],
        luggage: SkillLuggage
    ) -> None:
        """
        Extract variables from output and store in luggage.

        This is a simple implementation that looks for key-value patterns.
        Can be extended for more sophisticated extraction.

        Args:
            output: Output text to extract from
            variable_names: List of variable names to extract
            luggage: SkillLuggage to store variables
        """
        import re

        for var_name in variable_names:
            # Try to find pattern: var_name: value or var_name = value
            pattern = rf'{var_name}\s*[:=]\s*(.+?)(?:\n|$)'
            match = re.search(pattern, output, re.IGNORECASE)

            if match:
                value = match.group(1).strip()
                luggage.set_variable(var_name, value)
                if self.verbose:
                    self.console.print(f"[dim]  Extracted variable: {var_name} = {value}[/dim]")
            else:
                logger.warning(f"Could not extract variable: {var_name}")

    def get_final_output(self, luggage: SkillLuggage) -> str:
        """
        Get the final output from the last step.

        Args:
            luggage: SkillLuggage from execution

        Returns:
            Final output as string
        """
        if not luggage.step_outputs:
            return ""

        # Return the last step's output
        last_step = list(luggage.step_outputs.keys())[-1]
        return luggage.step_outputs[last_step]

    def export_results(
        self,
        luggage: SkillLuggage,
        output_path: str,
        format: str = "json"
    ) -> None:
        """
        Export results to a file.

        Args:
            luggage: SkillLuggage with results
            output_path: Path to save results
            format: Export format ("json", "text")
        """
        import json

        output_path = Path(output_path)

        if format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(luggage.to_dict(), f, indent=2, default=str)

        elif format == "text":
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"Skill: {luggage.skill_name}\n")
                f.write(f"Started: {luggage.started_at}\n\n")
                f.write("=" * 80 + "\n\n")

                for step_name, output in luggage.step_outputs.items():
                    f.write(f"## {step_name}\n\n")
                    f.write(output)
                    f.write("\n\n" + "=" * 80 + "\n\n")

        logger.info(f"Results exported to: {output_path}")
