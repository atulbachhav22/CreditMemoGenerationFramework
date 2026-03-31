# Skill Name: Financing Decision

## Metadata
- Version: 1.0.0
- Author: SkillEngine Team
- Description: Combines buyer credit risk and seller health scores to make a final invoice financing decision including discount rate and advance amount
- Tags: invoice-finance, decision, discount-rate, trade-finance

## Context
This is the final skill in the Invoice Financing pipeline. Both parallel upstream skills have completed:
- `buyer_credit_check` → how likely is the buyer to pay? (`buyer_risk_score`, `buyer_risk_tier`)
- `seller_health_check` → how healthy is the seller's business? (`seller_risk_score`, `seller_risk_tier`)

This skill combines both scores to answer three practical questions:
1. Should we finance this invoice? (APPROVE / DECLINE)
2. How much will we advance? (% of invoice face value)
3. What discount rate (fee) will we charge?

## Steps

### Step 1: Combine Risk Scores

**Instruction:**
From the pipeline context, collect the outputs from both parallel upstream skills:

From `buyer_credit_check`:
- `buyer_risk_score` (0–100)
- `buyer_risk_tier` (LOW RISK | MODERATE RISK | HIGH RISK)

From `seller_health_check`:
- `seller_risk_score` (0–100)
- `seller_risk_tier` (LOW RISK | MODERATE RISK | HIGH RISK)

From `invoice_validator`:
- `invoice_amount_usd`
- `days_until_due`
- `buyer_name`
- `seller_name`

Compute a `combined_risk_score` — a weighted average:
- Buyer risk weight: 60% (buyer payment is the primary risk)
- Seller risk weight: 40% (seller health is secondary risk)

`combined_risk_score` = (buyer_risk_score × 0.6) + (seller_risk_score × 0.4)

**Combined risk tier:**
- LOW RISK: 0–30
- MODERATE RISK: 31–55
- HIGH RISK: 56–100

**Variables to Extract:**
- combined_risk_score

**Expected Output:**
```json
{
  "combined_risk": {
    "buyer_risk_score": 20,
    "seller_risk_score": 20,
    "combined_risk_score": 20,
    "combined_risk_tier": "LOW RISK",
    "invoice_amount_usd": 185000,
    "days_until_due": 34,
    "buyer_name": "Global Motors Corp",
    "seller_name": "Apex Components Ltd"
  }
}
```

**Verification:**
- `combined_risk_score` must equal (buyer_risk_score × 0.6) + (seller_risk_score × 0.4)
- `combined_risk_tier` must match the score band
- All invoice fields must be present

---

### Step 2: Set Advance Rate and Discount Fee

**Instruction:**
Using the `combined_risk_score` and `days_until_due`, determine the financing terms.

**Advance rate** — percentage of invoice face value paid to seller upfront:

| Combined Risk Tier | Advance Rate |
|-------------------|-------------|
| LOW RISK | 90% |
| MODERATE RISK | 80% |
| HIGH RISK | 70% |

**Discount fee** — the fee charged for early payment, expressed as an annualised percentage. Calculate the actual fee for this specific invoice tenor:

Base annual rate by risk tier:
- LOW RISK: 6% per annum
- MODERATE RISK: 9% per annum
- HIGH RISK: 13% per annum

`fee_for_this_invoice_pct` = base_annual_rate × (days_until_due / 365)

Then compute in USD:
- `advance_amount_usd` = invoice_amount_usd × advance_rate
- `discount_fee_usd` = invoice_amount_usd × fee_for_this_invoice_pct
- `seller_receives_usd` = advance_amount_usd (upfront) + (invoice_amount_usd - advance_amount_usd - discount_fee_usd) on maturity

**Variables to Extract:**
- advance_rate
- advance_amount_usd
- discount_fee_usd

**Expected Output:**
```json
{
  "financing_terms": {
    "combined_risk_tier": "LOW RISK",
    "advance_rate_pct": 90,
    "base_annual_rate_pct": 6.0,
    "days_until_due": 34,
    "fee_for_this_invoice_pct": 0.559,
    "advance_amount_usd": 166500,
    "discount_fee_usd": 1034,
    "seller_receives_upfront_usd": 166500,
    "seller_receives_on_maturity_usd": 17466,
    "total_seller_receives_usd": 183966
  }
}
```

**Verification:**
- `advance_rate_pct` must be 90, 80, or 70
- `advance_amount_usd` = invoice_amount_usd × (advance_rate_pct / 100)
- `total_seller_receives_usd` must be less than `invoice_amount_usd`
- `fee_for_this_invoice_pct` = base_annual_rate_pct × days_until_due / 365

---

### Step 3: Produce Financing Decision Letter

**Instruction:**
Using all outputs from Steps 1 and 2, determine the final `financing_decision` and produce a short, clear decision letter for the seller.

**Decision rules:**
- APPROVE — `combined_risk_tier` is LOW RISK or MODERATE RISK
- DECLINE — `combined_risk_tier` is HIGH RISK

The decision letter must include:
1. **Decision** — APPROVED or DECLINED, in plain English
2. **Invoice Summary** — invoice number, amount, buyer, due date
3. **Terms** (if approved) — advance amount, fee, what the seller receives upfront and on maturity
4. **Reason** — 2–3 sentences explaining the decision based on buyer and seller assessments
5. **Next Steps** — what the seller needs to do to receive the funds

**Depends On:**
- 1
- 2

**Variables to Extract:**
- financing_decision

**Expected Output:**
A markdown-formatted financing decision letter as described above.

**Verification:**
- Letter must contain all 5 required sections
- Decision must be APPROVED or DECLINED
- If APPROVED, all financial figures must be included and correct
- `financing_decision` variable must be APPROVE or DECLINE

## Final Output Format
A markdown decision letter ready to send to the seller, plus a `financing_decision` variable in the pipeline luggage.

## Success Criteria
1. Combined risk score is correctly calculated from both parallel upstream scores
2. Advance rate and fee correctly follow the risk tier rules
3. All USD calculations are mathematically accurate
4. Decision letter is clear, professional, and contains all required sections
