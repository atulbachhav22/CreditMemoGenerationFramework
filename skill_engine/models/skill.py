"""
Skill model - Represents a complete skill definition parsed from Markdown.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class StepType(str, Enum):
    """Types of steps that can be executed."""
    INSTRUCTION = "instruction"  # LLM follows instructions
    LOAD_FILE = "load_file"  # Load a reference file
    VERIFICATION = "verification"  # Verify output against criteria
    TRANSFORMATION = "transformation"  # Transform data
    CUSTOM = "custom"  # Custom step type


class HttpMethod(str, Enum):
    """Supported HTTP methods for API context calls."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class ApiContextDefinition(BaseModel):
    """
    Defines an API endpoint to call for fetching context data.

    Used in both global (## API Context) and step-level (**API Context:**) sections.
    """

    alias: str = Field(
        ...,
        description="Key name used to store the API response in luggage"
    )

    endpoint: str = Field(
        ...,
        description="Full URL of the API endpoint"
    )

    method: HttpMethod = Field(
        default=HttpMethod.GET,
        description="HTTP method to use"
    )

    query_params: Optional[str] = Field(
        default=None,
        description="URL query parameters as key=value&key2=value2 string"
    )

    body: Optional[str] = Field(
        default=None,
        description="Request body as JSON string (for POST/PUT)"
    )

    extract: Optional[str] = Field(
        default=None,
        description="JSONPath dot-notation to extract a subset of the response (e.g., $.data.results)"
    )

    description: Optional[str] = Field(
        default=None,
        description="Human-readable description of what this API provides"
    )


class VerificationCriteria(BaseModel):
    """Criteria for verifying step output."""
    description: str = Field(
        ...,
        description="Human-readable description of what to verify"
    )

    rules: List[str] = Field(
        default_factory=list,
        description="List of specific rules that must be satisfied"
    )

    required_elements: List[str] = Field(
        default_factory=list,
        description="Elements that must be present in the output"
    )

    fail_action: str = Field(
        default="retry",
        description="Action to take if verification fails (retry, skip, halt)"
    )

    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts"
    )


class SkillStep(BaseModel):
    """
    Represents a single step in a Skill.

    Each step can contain instructions for the LLM, reference files to load,
    and verification criteria.
    """

    step_number: int = Field(
        ...,
        description="Sequential number of this step"
    )

    name: str = Field(
        ...,
        description="Name/title of this step"
    )

    description: Optional[str] = Field(
        default=None,
        description="Detailed description of what this step does"
    )

    instruction: str = Field(
        ...,
        description="The instruction or prompt for the LLM to execute"
    )

    step_type: StepType = Field(
        default=StepType.INSTRUCTION,
        description="Type of step"
    )

    reference_files: List[str] = Field(
        default_factory=list,
        description="List of file paths to load into context for this step"
    )

    expected_output_format: Optional[str] = Field(
        default=None,
        description="Description of expected output format (JSON, text, etc.)"
    )

    verification: Optional[VerificationCriteria] = Field(
        default=None,
        description="Verification criteria for this step's output"
    )

    depends_on: List[int] = Field(
        default_factory=list,
        description="Step numbers that must complete before this step"
    )

    variables_to_extract: List[str] = Field(
        default_factory=list,
        description="Variable names to extract from this step's output"
    )

    api_context: List["ApiContextDefinition"] = Field(
        default_factory=list,
        description="API endpoints to call for this step's context data"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for this step"
    )


class SkillMetadata(BaseModel):
    """Metadata about the Skill."""

    name: str = Field(
        ...,
        description="Name of the skill"
    )

    description: Optional[str] = Field(
        default=None,
        description="Description of what this skill does"
    )

    version: str = Field(
        default="1.0.0",
        description="Version of this skill"
    )

    author: Optional[str] = Field(
        default=None,
        description="Author of this skill"
    )

    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorizing this skill"
    )

    required_llm_capabilities: List[str] = Field(
        default_factory=list,
        description="LLM capabilities required (e.g., 'function_calling', 'long_context')"
    )

    estimated_tokens: Optional[int] = Field(
        default=None,
        description="Estimated token usage for this skill"
    )


class Skill(BaseModel):
    """
    Complete Skill definition.

    A Skill represents a complete workflow parsed from a Markdown file,
    containing metadata, context, steps, and verification criteria.
    """

    metadata: SkillMetadata = Field(
        ...,
        description="Metadata about this skill"
    )

    context: Optional[str] = Field(
        default=None,
        description="General context/background for this skill"
    )

    steps: List[SkillStep] = Field(
        default_factory=list,
        description="Ordered list of steps to execute"
    )

    global_reference_files: List[str] = Field(
        default_factory=list,
        description="Reference files available to all steps"
    )

    global_api_context: List[ApiContextDefinition] = Field(
        default_factory=list,
        description="API endpoints to call for global context data"
    )

    final_output_format: Optional[str] = Field(
        default=None,
        description="Description of the final output format"
    )

    success_criteria: Optional[str] = Field(
        default=None,
        description="Criteria for considering the entire skill successful"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "name": "Credit Memo Generator",
                    "description": "Generates credit memos from financial statements",
                    "version": "1.0.0",
                    "tags": ["finance", "credit", "analysis"]
                },
                "context": "This skill analyzes financial statements to generate credit memos.",
                "steps": [
                    {
                        "step_number": 1,
                        "name": "Extract Financial Data",
                        "instruction": "Extract key financial figures from the statement",
                        "reference_files": ["financial_statement.pdf"],
                        "verification": {
                            "description": "Ensure all required fields are extracted",
                            "required_elements": ["revenue", "expenses", "net_income"]
                        }
                    }
                ]
            }
        }

    def get_step(self, step_number: int) -> Optional[SkillStep]:
        """Get a specific step by number."""
        for step in self.steps:
            if step.step_number == step_number:
                return step
        return None

    def get_total_steps(self) -> int:
        """Get total number of steps."""
        return len(self.steps)

    def validate_dependencies(self) -> bool:
        """Validate that all step dependencies are satisfied."""
        step_numbers = {step.step_number for step in self.steps}
        for step in self.steps:
            for dep in step.depends_on:
                if dep not in step_numbers:
                    return False
        return True
