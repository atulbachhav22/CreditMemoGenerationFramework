"""
Pydantic schemas for the FastAPI skill execution API.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# --- Request schemas ---

class ExecuteSkillRequest(BaseModel):
    model_config = {"protected_namespaces": ()}

    llm_provider: Optional[str] = Field(
        default=None,
        description="LLM provider: 'openai' or 'anthropic'. Defaults to env DEFAULT_LLM_PROVIDER."
    )
    model_name: Optional[str] = Field(
        default=None,
        description="Model name (e.g. 'gpt-4', 'claude-3-5-sonnet-20241022'). Defaults to env DEFAULT_MODEL_NAME."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for the LLM provider. Falls back to env OPENAI_API_KEY or ANTHROPIC_API_KEY."
    )
    temperature: float = Field(
        default=0.0,
        description="Sampling temperature for the LLM."
    )
    initial_variables: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Initial variables to pass into skill execution."
    )
    reference_files: Optional[List[str]] = Field(
        default=None,
        description="File paths to inject as global reference files (e.g. paths returned by POST /documents)."
    )


# --- Response schemas ---

class StepSummary(BaseModel):
    step_number: int
    name: str
    instruction: str
    has_verification: bool


class SkillSummary(BaseModel):
    filename: str
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    author: Optional[str] = None
    tags: List[str] = []
    total_steps: int = 0


class SkillDetail(SkillSummary):
    context: Optional[str] = None
    steps: List[StepSummary] = []
    global_reference_files: List[str] = []
    final_output_format: Optional[str] = None
    success_criteria: Optional[str] = None


class ExecutionResult(BaseModel):
    skill_name: Optional[str] = None
    final_output: str = ""
    step_outputs: Dict[str, str] = {}
    variables: Dict[str, Any] = {}
    verification_results: Dict[str, bool] = {}
    execution_metadata: Dict[str, Any] = {}


class DocumentResponse(BaseModel):
    filename: str
    file_path: str
    size_bytes: int
    content_type: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
