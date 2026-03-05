"""
FastAPI application for executing SkillEngine skills via HTTP.

Run with:
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
"""

import json
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from skill_engine import SkillProcessor, SkillMarkdownParser, __version__
from api.schemas import (
    DocumentResponse,
    ExecuteSkillRequest,
    ExecutionResult,
    HealthResponse,
    SkillDetail,
    SkillSummary,
    StepSummary,
    Workflow,
    WorkflowExecutionResult,
    WorkflowNodeResult,
)

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
UPLOADS_DIR = PROJECT_ROOT / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

WORKFLOWS_DIR = PROJECT_ROOT / "workflows"
WORKFLOWS_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx", ".doc", ".json", ".csv", ".xml", ".yaml", ".yml", ".md"}

app = FastAPI(
    title="SkillEngine API",
    description="Lightweight API for listing and executing LLM-orchestrated skills.",
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = SkillMarkdownParser()


def _get_skill_files() -> dict[str, Path]:
    """Return a mapping of skill name (stem) -> file path for all .md skills."""
    if not SKILLS_DIR.exists():
        return {}
    return {
        p.stem: p
        for p in sorted(SKILLS_DIR.glob("*.md"))
        if p.name.lower() != "readme.md"
    }


# --- Endpoints ---


@app.get("/health", response_model=HealthResponse)
def health_check(): #:t to be used as a referen 
    return HealthResponse(status="ok", version=__version__)


@app.post("/documents", response_model=DocumentResponse, status_code=201)
def upload_document(file: UploadFile = File(...)):
    """
    Upload a documence file in skill execution.

    Supported formats: PDF, DOCX, TXT, JSON, CSV, XML, YAML, MD.
    The returned `file_path` can be passed as a reference file when executing a skill.
    """
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    dest = UPLOADS_DIR / file.filename
    try:
        with dest.open("wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    finally:
        file.file.close()

    return DocumentResponse(
        filename=file.filename,
        file_path=str(dest),
        size_bytes=dest.stat().st_size,
        content_type=file.content_type,
    )


@app.get("/documents", response_model=List[DocumentResponse])
def list_documents():
    """List all uploaded documents."""
    return [
        DocumentResponse(
            filename=f.name,
            file_path=str(f),
            size_bytes=f.stat().st_size,
        )
        for f in sorted(UPLOADS_DIR.iterdir())
        if f.is_file()
    ]


@app.get("/skills", response_model=List[SkillSummary])
def list_skills():
    """List all available skills from the skills/ directory."""
    results: list[SkillSummary] = []
    for stem, path in _get_skill_files().items():
        try:
            skill = parser.parse_file(str(path))
            results.append(
                SkillSummary(
                    filename=path.name,
                    name=skill.metadata.name,
                    description=skill.metadata.description,
                    version=skill.metadata.version,
                    author=skill.metadata.author,
                    tags=skill.metadata.tags,
                    total_steps=skill.get_total_steps(),
                )
            )
        except Exception as e:
            results.append(
                SkillSummary(
                    filename=path.name,
                    name=stem,
                    description=f"(parse error: {e})",
                )
            )
    return results


@app.get("/skills/{skill_name}", response_model=SkillDetail)
def get_skill(skill_name: str):
    """Get detailed information about a specific skill."""
    skills = _get_skill_files()
    if skill_name not in skills:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found.")

    try:
        skill = parser.parse_file(str(skills[skill_name]))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse skill: {e}")

    return SkillDetail(
        filename=skills[skill_name].name,
        name=skill.metadata.name,
        description=skill.metadata.description,
        version=skill.metadata.version,
        author=skill.metadata.author,
        tags=skill.metadata.tags,
        total_steps=skill.get_total_steps(),
        context=skill.context,
        steps=[
            StepSummary(
                step_number=s.step_number,
                name=s.name,
                instruction=s.instruction,
                has_verification=s.verification is not None,
            )
            for s in skill.steps
        ],
        global_reference_files=skill.global_reference_files,
        final_output_format=skill.final_output_format,
        success_criteria=skill.success_criteria,
    )


@app.post("/skills/{skill_name}/execute", response_model=ExecutionResult)
def execute_skill(skill_name: str, request: ExecuteSkillRequest = ExecuteSkillRequest()):
    """
    Execute a skill and return the results.

    This is a synchronous, blocking call — it will wait until all steps complete.
    """
    skills = _get_skill_files()
    if skill_name not in skills:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found.")

    # Resolve LLM configuration with fallbacks to environment variables
    llm_provider = request.llm_provider or os.getenv("DEFAULT_LLM_PROVIDER", "anthropic")
    model_name = request.model_name or os.getenv("DEFAULT_MODEL_NAME", "claude-3-5-sonnet-20241022")

    if request.api_key:
        api_key = request.api_key
    elif llm_provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
    else:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=400,
            detail=f"No API key provided and no environment variable set for provider '{llm_provider}'.",
        )

    try:
        processor = SkillProcessor(
            llm_provider=llm_provider,
            model_name=model_name,
            temperature=request.temperature,
            api_key=api_key,
            base_path=str(PROJECT_ROOT),
            verbose=False,
        )

        skill = parser.parse_file(str(skills[skill_name]))

        if request.reference_files:
            skill.global_reference_files.extend(request.reference_files)

        luggage = processor.execute_skill(
            skill,
            initial_variables=request.initial_variables,
        )

        final_output = processor.get_final_output(luggage)

        return ExecutionResult(
            skill_name=luggage.skill_name,
            final_output=final_output,
            step_outputs=luggage.step_outputs,
            variables=luggage.variables,
            verification_results=luggage.verification_results,
            execution_metadata=luggage.execution_metadata,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill execution failed: {e}")


# --- Workflow endpoints ---

@app.get("/workflows", response_model=List[Workflow])
def list_workflows():
    """List all saved workflows."""
    results = []
    for path in sorted(WORKFLOWS_DIR.glob("*.json")):
        try:
            results.append(Workflow(**json.loads(path.read_text(encoding="utf-8"))))
        except Exception:
            pass
    return results


@app.get("/workflows/{workflow_id}", response_model=Workflow)
def get_workflow(workflow_id: str):
    """Get a saved workflow by its ID."""
    path = WORKFLOWS_DIR / f"{workflow_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found.")
    try:
        return Workflow(**json.loads(path.read_text(encoding="utf-8")))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse workflow: {e}")


@app.post("/workflows", response_model=Workflow, status_code=201)
def save_workflow(workflow: Workflow):
    """
    Save a workflow. Assigns a new ID and created_at on first save.
    If the workflow already has an ID, updated_at is refreshed.
    """
    now = datetime.now(timezone.utc)

    if workflow.id and (WORKFLOWS_DIR / f"{workflow.id}.json").exists():
        # Update existing — preserve created_at
        existing = json.loads((WORKFLOWS_DIR / f"{workflow.id}.json").read_text(encoding="utf-8"))
        workflow.created_at = datetime.fromisoformat(existing["created_at"])
        workflow.updated_at = now
    else:
        workflow.id = str(uuid.uuid4())
        workflow.created_at = now
        workflow.updated_at = now

    path = WORKFLOWS_DIR / f"{workflow.id}.json"
    try:
        path.write_text(
            json.dumps(workflow.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save workflow: {e}")

    return workflow


def _topological_sort(workflow: Workflow) -> list[str]:
    """Return node IDs in topological execution order (Kahn's algorithm)."""
    from collections import defaultdict, deque

    in_degree = {n.id: 0 for n in workflow.nodes}
    adj: dict[str, list[str]] = defaultdict(list)

    for edge in workflow.edges:
        adj[edge.source].append(edge.target)
        in_degree[edge.target] = in_degree.get(edge.target, 0) + 1

    queue = deque(n_id for n_id, deg in in_degree.items() if deg == 0)
    order: list[str] = []

    while queue:
        n_id = queue.popleft()
        order.append(n_id)
        for neighbor in adj[n_id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(workflow.nodes):
        raise ValueError("Workflow contains a cycle — cannot execute.")

    return order


@app.post("/workflows/{workflow_id}/execute", response_model=WorkflowExecutionResult)
def execute_workflow(workflow_id: str, request: ExecuteSkillRequest = ExecuteSkillRequest()):
    """
    Execute a workflow by running each skill node in topological order.

    Variables produced by each skill are accumulated and passed into the
    next skill as initial_variables, so outputs can flow between steps.
    """
    path = WORKFLOWS_DIR / f"{workflow_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found.")

    try:
        workflow = Workflow(**json.loads(path.read_text(encoding="utf-8")))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse workflow: {e}")

    # Resolve LLM config (same logic as execute_skill)
    llm_provider = request.llm_provider or os.getenv("DEFAULT_LLM_PROVIDER", "anthropic")
    model_name = request.model_name or os.getenv("DEFAULT_MODEL_NAME", "claude-3-5-sonnet-20241022")

    if request.api_key:
        api_key = request.api_key
    elif llm_provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
    else:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=400,
            detail=f"No API key provided and no environment variable set for provider '{llm_provider}'.",
        )

    try:
        execution_order = _topological_sort(workflow)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    node_by_id = {n.id: n for n in workflow.nodes}
    skill_files = _get_skill_files()

    processor = SkillProcessor(
        llm_provider=llm_provider,
        model_name=model_name,
        temperature=request.temperature,
        api_key=api_key,
        base_path=str(PROJECT_ROOT),
        verbose=False,
    )

    # Variables accumulate across nodes so each skill sees prior outputs
    shared_variables: dict = dict(request.initial_variables or {})
    node_results: dict[str, WorkflowNodeResult] = {}

    for node_id in execution_order:
        node = node_by_id[node_id]

        if node.skill_name not in skill_files:
            node_results[node_id] = WorkflowNodeResult(
                node_id=node_id,
                skill_name=node.skill_name,
                label=node.label,
                error=f"Skill '{node.skill_name}' not found.",
            )
            continue

        try:
            skill = parser.parse_file(str(skill_files[node.skill_name]))

            if request.reference_files:
                skill.global_reference_files.extend(request.reference_files)

            luggage = processor.execute_skill(skill, initial_variables=dict(shared_variables))
            final_output = processor.get_final_output(luggage)

            # Accumulate variables for the next skill
            shared_variables.update(luggage.variables)
            # Also expose this skill's final output as a named variable
            shared_variables[f"{node.skill_name}_output"] = final_output

            node_results[node_id] = WorkflowNodeResult(
                node_id=node_id,
                skill_name=node.skill_name,
                label=node.label,
                final_output=final_output,
                step_outputs=luggage.step_outputs,
                variables=luggage.variables,
                verification_results=luggage.verification_results,
                execution_metadata=luggage.execution_metadata,
            )

        except Exception as e:
            node_results[node_id] = WorkflowNodeResult(
                node_id=node_id,
                skill_name=node.skill_name,
                label=node.label,
                error=str(e),
            )

    completed = all(r.error is None for r in node_results.values())

    return WorkflowExecutionResult(
        workflow_id=workflow_id,
        workflow_name=workflow.name,
        execution_order=execution_order,
        node_results=node_results,
        completed=completed,
    )
