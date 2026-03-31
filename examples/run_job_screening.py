"""
Autonomous Agent Demo — Job Application Screening Pipeline
==========================================================

The simplest demo of the multi-skill parallel pipeline.

Pipeline:
  [resume_parser]                    ← Wave 1: read and structure the resume
          │
  ┌───────┴────────┐
  [skills_matcher] [background_check] ← Wave 2: PARALLEL — run at the same time
  └───────┬────────┘
  [hiring_decision]                  ← Wave 3: combine both results → recommend

Why parallel matters here:
  - skills_matcher asks  "Does the candidate have the right skills?"
  - background_check asks "Is the candidate's history consistent?"
  - These two questions are completely independent — no reason to wait.
  - Running them in parallel cuts Wave 2 time roughly in half.

Run:
    cd "c:/My AI Projects/CreditMemoGenerationFramework"
    python examples/run_job_screening.py
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from skill_engine import PipelineOrchestrator

load_dotenv()

console = Console()


# ── Candidate resume ──────────────────────────────────────────────────────────
CANDIDATE = {
    "full_name": "Alex Rivera",
    "email": "alex.rivera@email.com",
    "phone": "+1-555-0142",
    "location": "Austin, TX, USA",
    "current_job_title": "Senior Software Engineer",
    "current_employer": "TechCorp Inc",

    # Employment history (most recent first)
    "employment_history": [
        {
            "employer": "TechCorp Inc",
            "title": "Senior Software Engineer",
            "start": "2021",
            "end": "Present"
        },
        {
            "employer": "StartupXYZ",
            "title": "Software Engineer",
            "start": "2018",
            "end": "2021"
        }
    ],

    # Skills on resume
    "technical_skills": ["Python", "FastAPI", "PostgreSQL", "AWS", "Docker", "React"],
    "soft_skills": ["team leadership", "agile project management"],

    # Education
    "degree": "Bachelor of Science",
    "field": "Computer Science",
    "institution": "University of Texas at Austin",
    "graduation_year": 2018,
}

# ── Job requirements (what we're hiring for) ──────────────────────────────────
JOB_REQUIREMENTS = {
    "job_title": "Senior Backend Engineer",
    "min_years_experience": 4,
    "min_education": "Bachelor",
    "required_skills": ["Python", "PostgreSQL", "AWS", "Docker", "Kubernetes"],
    "preferred_skills": ["React", "Terraform"],
}


def main():
    # ── 1. Create orchestrator ────────────────────────────────────────────────
    orchestrator = PipelineOrchestrator(
        skills_dir=str(ROOT / "skills"),
        base_path=str(ROOT),

        # Option A — Anthropic Claude (recommended)
        llm_provider="anthropic",
        model_name="claude-sonnet-4-6",
        api_key=os.getenv("ANTHROPIC_API_KEY"),

        # Option B — OpenAI
        # llm_provider="openai",
        # model_name="gpt-4o",
        # api_key=os.getenv("OPENAI_API_KEY"),

        max_workers=2,   # 2 is enough — only 2 skills run in parallel
        verbose=True,
    )

    # ── 2. Show what we're screening ─────────────────────────────────────────
    console.print(Panel.fit(
        f"[bold cyan]Job Application Screening Agent[/bold cyan]\n\n"
        f"[bold]Candidate:[/bold] {CANDIDATE['full_name']} — {CANDIDATE['current_job_title']}\n"
        f"[bold]Applying for:[/bold] {JOB_REQUIREMENTS['job_title']}\n"
        f"[bold]Required skills:[/bold] {', '.join(JOB_REQUIREMENTS['required_skills'])}",
        border_style="cyan",
    ))

    # ── 3. Run the pipeline ───────────────────────────────────────────────────
    result = orchestrator.execute_workflow_file(
        workflow_path=str(ROOT / "workflows" / "Job Application Screening Workflow.json"),
        initial_variables={**CANDIDATE, **{"job_requirements": JOB_REQUIREMENTS}},
    )

    # ── 4. Show execution waves ───────────────────────────────────────────────
    console.print()
    console.rule("[bold]What happened[/bold]")

    node_labels = {
        "resume_parser-2001": "Resume Parser",
        "skills_matcher-2002": "Skills Matcher",
        "background_check-2003": "Background Check",
        "hiring_decision-2004": "Hiring Decision",
    }

    wave_table = Table(show_header=True, header_style="bold magenta", show_lines=True)
    wave_table.add_column("Wave", justify="center", style="bold", width=6)
    wave_table.add_column("Skill(s) Running", style="cyan")
    wave_table.add_column("Mode", style="bold", width=18)
    wave_table.add_column("Why parallel?")

    wave_notes = [
        "Entry point — must run first",
        "Independent questions — no need to wait for each other",
        "Needs answers from BOTH parallel skills",
    ]

    for i, wave in enumerate(result.execution_order, 1):
        labels = "\n".join(node_labels.get(nid, nid) for nid in wave)
        mode = "[bold yellow]⟳ PARALLEL[/bold yellow]" if len(wave) > 1 else "[white]sequential[/white]"
        wave_table.add_row(str(i), labels, mode, wave_notes[i - 1])

    console.print(wave_table)

    # ── 5. Show scores from parallel skills ──────────────────────────────────
    console.print()
    score_table = Table(title="Outputs from Parallel Skills", show_header=True, header_style="bold magenta")
    score_table.add_column("Skill", style="cyan", width=20)
    score_table.add_column("Key Output", style="bold")

    skills_score = _get(result, "skills_match_score", "—")
    skills_grade = _get(result, "skills_match_grade", "—")
    bg_status = _get(result, "background_status", "—")
    bg_flags = _get(result, "flags_found", "—")

    score_table.add_row(
        "Skills Matcher",
        f"Score: {skills_score}/100  |  Grade: {skills_grade}"
    )
    score_table.add_row(
        "Background Check",
        f"Status: {bg_status}  |  Flags found: {bg_flags}"
    )

    console.print(score_table)

    # ── 6. Final decision ─────────────────────────────────────────────────────
    recommendation = _get(result, "hiring_recommendation", "N/A")
    overall_score = _get(result, "overall_score", "—")

    color = {
        "ADVANCE_TO_INTERVIEW": "bold green",
        "ADVANCE_WITH_NOTE": "bold yellow",
        "HOLD_FOR_REVIEW": "bold orange3",
        "REJECT": "bold red",
    }.get(str(recommendation), "white")

    console.print()
    console.print(Panel(
        f"[{color}]{recommendation}[/{color}]\n"
        f"[dim]Overall Score: {overall_score}/100  |  "
        f"Duration: {result.duration_seconds:.1f}s[/dim]",
        title="[bold]Hiring Recommendation[/bold]",
        border_style="green" if result.success else "red",
    ))

    # ── 7. Print the hiring report ────────────────────────────────────────────
    if result.final_luggage.step_outputs:
        last_step = list(result.final_luggage.step_outputs.keys())[-1]
        console.print()
        console.rule("[bold]Hiring Report[/bold]")
        console.print(result.final_luggage.step_outputs[last_step])


def _get(result, key, default):
    """Find a variable in any node's luggage."""
    val = result.final_luggage.variables.get(key)
    if val is not None:
        return val
    for luggage in result.node_luggages.values():
        val = luggage.variables.get(key)
        if val is not None:
            return val
    return default


if __name__ == "__main__":
    main()
