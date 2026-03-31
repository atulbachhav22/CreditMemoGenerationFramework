# Skill Name: Seller Health Check

## Metadata
- Version: 1.0.0
- Author: SkillEngine Team
- Description: Assesses the financial health of the seller (the company requesting invoice financing) — runs in parallel with buyer_credit_check
- Tags: seller, financial-health, invoice-finance, concentration-risk

## Context
This skill runs in parallel with `buyer_credit_check` after `invoice_validator` completes.

The central question here is: **Is the seller a financially healthy business we can trust?**

Even if the buyer is creditworthy, the financier needs to know the seller is legitimate and not in financial distress. Key concerns:
- Is the seller's business stable enough to handle a dispute or clawback?
- Is this invoice a normal part of their business, or unusually large?
- Are they dangerously dependent on one buyer (concentration risk)?

## Steps

### Step 1: Assess Seller Financial Stability

**Instruction:**
Using `seller_name`, `invoice_amount_usd`, and any financial data in the pipeline context, assess the seller's financial health across three dimensions:

**Dimension 1 — Business Stability**
- `years_in_business` — estimate from context, or state UNKNOWN
- `business_maturity` — ESTABLISHED (>5 years) | GROWING (2–5 years) | EARLY_STAGE (<2 years) | UNKNOWN
- `revenue_stability` — STABLE | VARIABLE | UNKNOWN

**Dimension 2 — Invoice Size vs Business Scale**
- `invoice_as_pct_of_monthly_revenue` — estimate: invoice_amount_usd as a % of the seller's estimated monthly revenue
- `invoice_size_assessment` — NORMAL (<20% of monthly revenue) | LARGE (20–50%) | OVERSIZED (>50%)

**Dimension 3 — Buyer Concentration Risk**
- `concentration_risk` — risk that the seller depends too heavily on one buyer:
  - LOW — buyer appears to be one of many customers
  - MEDIUM — buyer may represent a significant portion of revenue
  - HIGH — seller appears heavily dependent on this single buyer

Include a one-line `rationale` for each dimension.

**Expected Output:**
```json
{
  "seller_assessment": {
    "seller_name": "Apex Components Ltd",
    "business_maturity": "ESTABLISHED",
    "revenue_stability": "STABLE",
    "invoice_as_pct_of_monthly_revenue": 18,
    "invoice_size_assessment": "NORMAL",
    "concentration_risk": "LOW",
    "rationale": {
      "business_maturity": "Industrial components supplier — typically established businesses with long customer relationships",
      "revenue_stability": "B2B manufacturing suppliers tend to have stable, contract-driven revenue",
      "invoice_size_assessment": "$185K invoice is within normal range for an established industrial supplier",
      "concentration_risk": "Automotive OEMs typically spread their supply base across many suppliers"
    }
  }
}
```

**Verification:**
- `business_maturity` must be ESTABLISHED | GROWING | EARLY_STAGE | UNKNOWN
- `invoice_size_assessment` must be NORMAL | LARGE | OVERSIZED
- `concentration_risk` must be LOW | MEDIUM | HIGH
- All `rationale` entries must be non-empty strings

---

### Step 2: Calculate Seller Risk Score

**Instruction:**
Using the seller assessment from Step 1, calculate a `seller_risk_score` from 0 (very low risk) to 100 (very high risk).

**Scoring table:**

| Factor | Low Risk | Medium Risk | High Risk |
|--------|----------|-------------|-----------|
| business_maturity | ESTABLISHED = 5 | GROWING = 15 | EARLY_STAGE/UNKNOWN = 30 |
| revenue_stability | STABLE = 5 | VARIABLE = 20 | UNKNOWN = 25 |
| invoice_size_assessment | NORMAL = 5 | LARGE = 15 | OVERSIZED = 30 |
| concentration_risk | LOW = 5 | MEDIUM = 15 | HIGH = 25 |

Sum all four. Total is the `seller_risk_score` (max 110, but cap at 100).

**Seller risk tier:**
- LOW RISK: 0–30
- MODERATE RISK: 31–55
- HIGH RISK: 56–100

**Variables to Extract:**
- seller_risk_score
- seller_risk_tier

**Expected Output:**
```json
{
  "seller_risk_result": {
    "seller_risk_score": 20,
    "seller_risk_tier": "LOW RISK",
    "score_breakdown": {
      "business_maturity": 5,
      "revenue_stability": 5,
      "invoice_size": 5,
      "concentration_risk": 5
    },
    "summary": "Apex Components Ltd appears to be an established, stable B2B supplier with a normally-sized invoice and low buyer concentration risk."
  }
}
```

**Verification:**
- `seller_risk_score` must be between 0 and 100
- Score breakdown components must sum to `seller_risk_score` (before capping)
- `seller_risk_tier` must match the score band
- `summary` must be at least 1 sentence

## Final Output Format
A `seller_risk_result` with score, tier, and summary passed into the pipeline luggage.

## Success Criteria
1. All three seller dimensions are assessed with clear rationale
2. Score arithmetic is correct
3. Risk tier correctly reflects the score band
