"""
Autonomous Agent Demo — Invoice Financing Pipeline
===================================================

The simplest financial domain demo of the parallel pipeline.

Pipeline:
  [invoice_validator]                      ← Wave 1: validate the invoice
           │
  ┌────────┴─────────┐
  [buyer_credit_check] [seller_health_check] ← Wave 2: PARALLEL
  └────────┬─────────┘
  [financing_decision]                     ← Wave 3: decision + terms

Why parallel?
  buyer_credit_check  asks: "Will the buyer PAY this invoice?"
  seller_health_check asks: "Is the SELLER a healthy business?"
  → Completely independent questions. No reason to run one after the other.

Run:
    cd "c:/My AI Projects/CreditMemoGenerationFramework"
    python examples/run_invoice_financing.py
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


# ── Invoice submitted for financing ──────────────────────────────────────────
INVOICE = {
    "invoice_number": "INV-2026-00842",
    "invoice_date": "2026-03-01",
    "due_date": "2026-04-30",
    "seller_name": "Apex Components Ltd",
    "buyer_name": "Global Motors Corp",
    "invoice_amount_usd": 185000,
    "currency": "USD",
    "description": "Industrial hydraulic components — Purchase Order #PO-88821",
    "payment_terms": "Net 60",
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

        max_workers=2,
        verbose=True,
    )

    # ── 2. Show invoice ───────────────────────────────────────────────────────
    console.print(Panel.fit(
        "[bold cyan]Invoice Financing Agent[/bold cyan]\n\n"
        f"[bold]Invoice:[/bold]  {INVOICE['invoice_number']}\n"
        f"[bold]Seller:[/bold]   {INVOICE['seller_name']}\n"
        f"[bold]Buyer:[/bold]    {INVOICE['buyer_name']}\n"
        f"[bold]Amount:[/bold]   ${INVOICE['invoice_amount_usd']:,}\n"
        f"[bold]Due:[/bold]      {INVOICE['due_date']}  ({INVOICE['payment_terms']})",
        border_style="cyan",
    ))

    # ── 3. Run the pipeline ───────────────────────────────────────────────────
    result = orchestrator.execute_workflow_file(
        workflow_path=str(ROOT / "workflows" / "Invoice Financing Workflow.json"),
        initial_variables=INVOICE,
    )

    # ── 4. Execution wave summary ─────────────────────────────────────────────
    console.print()
    console.rule("[bold]What happened[/bold]")

    node_labels = {
        "invoice_validator-3001": "Invoice Validator",
        "buyer_credit_check-3002": "Buyer Credit Check",
        "seller_health_check-3003": "Seller Health Check",
        "financing_decision-3004": "Financing Decision",
    }

    wave_table = Table(show_header=True, header_style="bold magenta", show_lines=True)
    wave_table.add_column("Wave", justify="center", style="bold", width=6)
    wave_table.add_column("Skill(s)", style="cyan")
    wave_table.add_column("Mode", style="bold", width=18)
    wave_table.add_column("Question being answered")

    wave_notes = [
        "Is this invoice valid and eligible?",
        "Will the BUYER pay?  |  Is the SELLER healthy?",
        "Should we finance, and at what price?",
    ]

    for i, wave in enumerate(result.execution_order, 1):
        labels = "\n".join(node_labels.get(nid, nid) for nid in wave)
        mode = "[bold yellow]⟳ PARALLEL[/bold yellow]" if len(wave) > 1 else "[white]sequential[/white]"
        wave_table.add_row(str(i), labels, mode, wave_notes[i - 1])

    console.print(wave_table)

    # ── 5. Scores from parallel skills ────────────────────────────────────────
    console.print()
    score_table = Table(
        title="Parallel Risk Scores", show_header=True, header_style="bold magenta"
    )
    score_table.add_column("Skill", style="cyan", width=22)
    score_table.add_column("Score", justify="right", width=8)
    score_table.add_column("Risk Tier", style="bold")

    buyer_score = _get(result, "buyer_risk_score", "—")
    buyer_tier  = _get(result, "buyer_risk_tier",  "—")
    seller_score = _get(result, "seller_risk_score", "—")
    seller_tier  = _get(result, "seller_risk_tier",  "—")
    combined     = _get(result, "combined_risk_score", "—")

    score_table.add_row("Buyer Credit Check",  str(buyer_score),  str(buyer_tier))
    score_table.add_row("Seller Health Check", str(seller_score), str(seller_tier))
    score_table.add_row("[bold]Combined (60/40)[/bold]", f"[bold]{combined}[/bold]", "")

    console.print(score_table)

    # ── 6. Financing terms ────────────────────────────────────────────────────
    decision      = _get(result, "financing_decision", "N/A")
    advance_amt   = _get(result, "advance_amount_usd", "—")
    discount_fee  = _get(result, "discount_fee_usd", "—")
    advance_rate  = _get(result, "advance_rate", "—")

    color = "bold green" if str(decision) == "APPROVE" else "bold red"

    console.print()
    console.print(Panel(
        f"[{color}]{decision}[/{color}]\n\n"
        + (
            f"[bold]Advance rate:[/bold]   {advance_rate}%\n"
            f"[bold]Advance amount:[/bold]  ${advance_amt:,}\n"
            f"[bold]Discount fee:[/bold]    ${discount_fee:,}\n"
            if str(decision) == "APPROVE" and isinstance(advance_amt, (int, float))
            else ""
        )
        + f"\n[dim]Duration: {result.duration_seconds:.1f}s[/dim]",
        title="[bold]Financing Decision[/bold]",
        border_style="green" if str(decision) == "APPROVE" else "red",
    ))

    # ── 7. Decision letter ────────────────────────────────────────────────────
    if result.final_luggage.step_outputs:
        last_step = list(result.final_luggage.step_outputs.keys())[-1]
        console.print()
        console.rule("[bold]Decision Letter[/bold]")
        console.print(result.final_luggage.step_outputs[last_step])


def _get(result, key, default):
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
