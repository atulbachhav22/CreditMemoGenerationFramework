"""
Autonomous Agent Demo — Merchant Onboarding Pipeline
=====================================================

Demonstrates the PipelineOrchestrator executing:
  workflows/Merchant Onboarding Workflow.json

Pipeline structure:

  [business_verification]              ← Wave 1  (sequential start)
           │
    ┌──────┴───────┐
[financial_health] [industry_risk]     ← Wave 2  (PARALLEL)
    └──────┬───────┘
  [fraud_risk_scoring]                 ← Wave 3  (sequential, waits for both)
           │
  [merchant_decision]                  ← Wave 4  (sequential end)

Key difference from the Credit Memo pipeline:
  - The PARALLEL wave is Wave 2 (earlier in the flow)
  - fraud_risk_scoring has TWO predecessors — it waits for BOTH parallel nodes
  - The pipeline includes hard-block logic (sanctions / prohibited MCC)

Run:
    cd "c:/My AI Projects/CreditMemoGenerationFramework"
    python examples/run_merchant_onboarding.py
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
from rich.columns import Columns

from skill_engine import PipelineOrchestrator

load_dotenv()

console = Console()


# ── Merchant application data seeded into the pipeline ───────────────────────
MERCHANT_APPLICATION = {
    # Identity
    "merchant_name": "Meridian Retail Solutions Ltd",
    "trading_name": "Meridian Pay",
    "registration_number": "RC-789456",
    "registration_country": "United Kingdom",
    "registration_date": "2018-03-15",
    "business_type": "PRIVATE_LIMITED",
    "registered_address": "12 Commerce Lane, London, EC2A 4TP",
    "primary_contact": "Sarah Thompson",
    "contact_email": "sarah.thompson@meridianpay.co.uk",

    # Business profile
    "industry": "Consumer electronics — online and in-store retail",
    "business_model": "MIXED",

    # Financials (most recent fiscal year)
    "annual_revenue_usd": 4200000,
    "gross_profit_margin_pct": 42.5,
    "net_profit_margin_pct": 8.2,
    "revenue_growth_yoy_pct": 18.5,
    "cash_and_equivalents_usd": 420000,
    "current_ratio": 1.85,
    "working_capital_usd": 280000,

    # Processing history
    "requested_monthly_volume_usd": 280000,
    "historical_monthly_volume_usd": 245000,
    "avg_transaction_value_usd": 85,
    "card_not_present_pct": 72,
    "chargeback_rate_pct": 0.18,
    "refund_rate_pct": 2.1,

    # Ownership
    "director_1_name": "Sarah Thompson",
    "director_1_ownership_pct": 60,
    "director_1_id_type": "PASSPORT",
    "director_2_name": "James Okafor",
    "director_2_ownership_pct": 40,
    "director_2_id_type": "PASSPORT",
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

        max_workers=4,
        verbose=True,
    )

    # ── 2. Print application summary ─────────────────────────────────────────
    console.print(Panel.fit(
        "[bold cyan]Autonomous Merchant Onboarding Agent[/bold cyan]\n"
        f"[dim]Applicant: {MERCHANT_APPLICATION['merchant_name']}[/dim]\n"
        f"[dim]Industry:  {MERCHANT_APPLICATION['industry']}[/dim]\n"
        f"[dim]Requested monthly volume: ${MERCHANT_APPLICATION['requested_monthly_volume_usd']:,}[/dim]",
        border_style="cyan",
    ))

    # ── 3. Run the pipeline ───────────────────────────────────────────────────
    result = orchestrator.execute_workflow_file(
        workflow_path=str(ROOT / "workflows" / "Merchant Onboarding Workflow.json"),
        initial_variables=MERCHANT_APPLICATION,
    )

    # ── 4. Print execution summary ────────────────────────────────────────────
    console.print()
    console.rule("[bold]Execution Summary[/bold]")

    # Wave table
    wave_table = Table(title="Execution Waves", show_header=True, header_style="bold magenta", show_lines=True)
    wave_table.add_column("Wave", justify="center", style="bold")
    wave_table.add_column("Skill(s)", style="cyan")
    wave_table.add_column("Mode", style="bold")
    wave_table.add_column("Waited For")

    wave_labels = {
        "business_verification-1774930001001": "Business Verification",
        "financial_health_check-1774930002001": "Financial Health Check",
        "industry_risk_assessment-1774930003001": "Industry Risk Assessment",
        "fraud_risk_scoring-1774930004001": "Fraud Risk Scoring",
        "merchant_decision-1774930005001": "Merchant Decision",
    }

    for i, wave in enumerate(result.execution_order, 1):
        labels = [wave_labels.get(nid, nid.split("-")[0]) for nid in wave]
        mode = "[bold yellow]PARALLEL[/bold yellow]" if len(wave) > 1 else "[white]sequential[/white]"
        waited = "—" if i == 1 else f"Wave {i - 1}"
        wave_table.add_row(str(i), "\n".join(labels), mode, waited)

    console.print(wave_table)

    # Score summary table
    console.print()
    score_table = Table(title="Risk Scores from Parallel Skills", show_header=True, header_style="bold magenta")
    score_table.add_column("Skill", style="cyan")
    score_table.add_column("Key Score / Status", style="bold")

    scores = [
        ("Business Verification", f"KYC: {_extract(result, 'kyc_risk_level', 'N/A')}  |  Sanctions: {_extract(result, 'sanctions_status', 'N/A')}"),
        ("Financial Health Check", f"Score: {_extract(result, 'financial_health_score', 'N/A')} / 100  |  Reserve: {_extract(result, 'recommended_rolling_reserve_pct', 'N/A')}%"),
        ("Industry Risk Assessment", f"Score: {_extract(result, 'industry_risk_score', 'N/A')} / 100  |  MCC: {_extract(result, 'mcc_risk_category', 'N/A')}"),
        ("Fraud Risk Scoring", f"Score: {_extract(result, 'fraud_risk_score', 'N/A')} / 100  |  {_extract(result, 'fraud_risk_level', 'N/A')}"),
    ]
    for skill, score in scores:
        score_table.add_row(skill, score)

    console.print(score_table)

    # Final decision
    decision = _extract(result, 'onboarding_decision', 'N/A')
    decision_color = {
        "APPROVE": "bold green",
        "APPROVE_WITH_CONDITIONS": "bold yellow",
        "MANUAL_REVIEW": "bold orange3",
        "DECLINE": "bold red",
    }.get(str(decision), "white")

    console.print()
    console.print(Panel(
        f"[{decision_color}]{decision}[/{decision_color}]\n\n"
        f"[dim]Duration: {result.duration_seconds:.1f}s  |  "
        f"Nodes: {len(result.completed_nodes)}  |  "
        f"Parallel waves: {sum(1 for w in result.execution_order if len(w) > 1)}[/dim]",
        title="[bold]Final Onboarding Decision[/bold]",
        border_style="green" if result.success else "red",
    ))

    # ── 5. Show final offer letter output ────────────────────────────────────
    final_luggage = result.final_luggage
    if final_luggage.step_outputs:
        last_step = list(final_luggage.step_outputs.keys())[-1]
        console.print()
        console.rule("[bold]Merchant Offer Letter[/bold]")
        console.print(f"[dim]Generated by: {last_step}[/dim]\n")
        console.print(final_luggage.step_outputs[last_step])


def _extract(result, key: str, default):
    """Helper: find a variable value anywhere in the pipeline luggages."""
    # Check final merged luggage first
    val = result.final_luggage.variables.get(key)
    if val is not None:
        return val
    # Fall back to per-node luggages
    for luggage in result.node_luggages.values():
        val = luggage.variables.get(key)
        if val is not None:
            return val
    return default


if __name__ == "__main__":
    main()
