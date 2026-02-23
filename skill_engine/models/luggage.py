"""
SkillLuggage - State management for Skill execution.

The Luggage carries data between steps, maintaining context and outputs.
"""

import json
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SkillLuggage(BaseModel):
    """
    State container that carries data between skill execution steps.

    The Luggage acts as a shared context, storing:
    - Variables and intermediate results
    - File paths and loaded content
    - Step outputs
    - Verification results
    """

    # Core state
    variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value store for variables used across steps"
    )

    step_outputs: Dict[str, str] = Field(
        default_factory=dict,
        description="Output from each executed step, keyed by step name/number"
    )

    loaded_files: Dict[str, str] = Field(
        default_factory=dict,
        description="Content of loaded reference files, keyed by file path"
    )

    verification_results: Dict[str, bool] = Field(
        default_factory=dict,
        description="Results of verification checks, keyed by step name"
    )

    api_responses: Dict[str, Any] = Field(
        default_factory=dict,
        description="Responses from API context calls, keyed by alias"
    )

    # Metadata
    execution_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about the execution (timestamps, model used, etc.)"
    )

    # Session info
    skill_name: Optional[str] = Field(
        default=None,
        description="Name of the skill being executed"
    )

    started_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when skill execution started"
    )

    current_step: Optional[str] = Field(
        default=None,
        description="Name or identifier of the currently executing step"
    )

    class Config:
        arbitrary_types_allowed = True

    def set_variable(self, key: str, value: Any) -> None:
        """Set a variable in the luggage."""
        self.variables[key] = value

    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get a variable from the luggage."""
        return self.variables.get(key, default)

    def add_step_output(self, step_name: str, output: str) -> None:
        """Store output from a completed step."""
        self.step_outputs[step_name] = output

    def get_step_output(self, step_name: str) -> Optional[str]:
        """Retrieve output from a previous step."""
        return self.step_outputs.get(step_name)

    def load_file_content(self, file_path: str, content: str) -> None:
        """Store loaded file content."""
        self.loaded_files[file_path] = content

    def get_file_content(self, file_path: str) -> Optional[str]:
        """Retrieve loaded file content."""
        return self.loaded_files.get(file_path)

    def record_verification(self, step_name: str, passed: bool) -> None:
        """Record verification result for a step."""
        self.verification_results[step_name] = passed

    def store_api_response(self, alias: str, data: Any) -> None:
        """Store an API response in luggage."""
        self.api_responses[alias] = data

    def get_api_response(self, alias: str) -> Optional[Any]:
        """Retrieve a stored API response."""
        return self.api_responses.get(alias)

    def get_context_summary(self) -> str:
        """Generate a text summary of current luggage state for LLM context."""
        summary_parts = []

        if self.variables:
            summary_parts.append("## Current Variables:")
            for key, value in self.variables.items():
                summary_parts.append(f"- {key}: {value}")

        if self.step_outputs:
            summary_parts.append("\n## Previous Step Outputs:")
            for step, output in self.step_outputs.items():
                summary_parts.append(f"### {step}")
                summary_parts.append(output[:500] + "..." if len(output) > 500 else output)

        if self.loaded_files:
            summary_parts.append("\n## Loaded Reference Files:")
            for file_path in self.loaded_files.keys():
                summary_parts.append(f"- {file_path}")

        if self.api_responses:
            summary_parts.append("\n## API Context Data:")
            for alias, data in self.api_responses.items():
                summary_parts.append(f"### {alias}")
                if isinstance(data, (dict, list)):
                    data_str = json.dumps(data, indent=2, default=str)
                else:
                    data_str = str(data)
                if len(data_str) > 1000:
                    data_str = data_str[:1000] + "... [truncated]"
                summary_parts.append(data_str)

        return "\n".join(summary_parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert luggage to dictionary format."""
        return self.model_dump()
