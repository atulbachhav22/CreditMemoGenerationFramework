# Skill Name: Buyer Credit Check

## Metadata
- Version: 1.0.0
- Author: SkillEngine Team
- Description: Assesses the creditworthiness of the buyer (the company that owes payment on the invoice) — runs in parallel with seller_health_check
- Tags: credit, buyer, invoice-finance, payment-risk

## Context
This skill runs in parallel with `seller_health_check` after `invoice_validator` completes.

The central question here is: **Will the buyer actually pay this invoice?**

In invoice financing, the financier is effectively taking on the buyer's payment risk. If the buyer defaults, the financier loses money. This skill scores that risk.

## Steps

### Step 1: Assess Buyer Payment Risk

**Instruction:**
Using the `buyer_name` from the pipeline context, assess the buyer's ability and willingness to pay the invoice.

Evaluate the following factors and assign a rating to each:

- `buyer_size` — estimate the buyer's size: LARGE_ENTERPRISE (>$1B revenue) | MID_MARKET ($50M–$1B) | SME (<$50M) — base this on the buyer's name and any context available
- `industry_payment_norms` — typical payment behaviour in the buyer's industry: PROMPT (pays before due date) | STANDARD (pays on time) | SLOW (often pays late)
- `estimated_credit_rating` — estimated credit quality: INVESTMENT_GRADE | NEAR_INVESTMENT_GRADE | SPECULATIVE | UNKNOWN
- `payment_history_indicator` — based on industry reputation: STRONG | AVERAGE | WEAK | UNKNOWN
- `buyer_financial_stability` — overall stability assessment: STABLE | MODERATE | UNCERTAIN

For each factor, include a one-line `rationale`.

**Expected Output:**
```json
{
  "buyer_assessment": {
    "buyer_name": "Global Motors Corp",
    "buyer_size": "LARGE_ENTERPRISE",
    "industry_payment_norms": "STANDARD",
    "estimated_credit_rating": "INVESTMENT_GRADE",
    "payment_history_indicator": "STRONG",
    "buyer_financial_stability": "STABLE",
    "rationale": {
      "buyer_size": "Global Motors Corp is a major automotive manufacturer with revenues well above $1B",
      "industry_payment_norms": "Automotive OEMs typically pay on standard Net 30–60 terms",
      "estimated_credit_rating": "Large established manufacturers generally carry investment-grade credit",
      "payment_history_indicator": "Large automotive companies maintain strong supplier payment track records",
      "buyer_financial_stability": "Diversified global automotive company with stable long-term operations"
    }
  }
}
```

**Verification:**
- `buyer_size` must be LARGE_ENTERPRISE | MID_MARKET | SME
- `estimated_credit_rating` must be INVESTMENT_GRADE | NEAR_INVESTMENT_GRADE | SPECULATIVE | UNKNOWN
- `buyer_financial_stability` must be STABLE | MODERATE | UNCERTAIN
- All `rationale` fields must be non-empty strings

---

### Step 2: Calculate Buyer Risk Score

**Instruction:**
Using the buyer assessment from Step 1, calculate a `buyer_risk_score` from 0 (very low risk) to 100 (very high risk).

**Scoring table (higher score = higher risk of non-payment):**

| Factor | Low Risk | Medium Risk | High Risk |
|--------|----------|-------------|-----------|
| buyer_size | LARGE_ENTERPRISE = 5 | MID_MARKET = 15 | SME = 25 |
| estimated_credit_rating | INVESTMENT_GRADE = 5 | NEAR_INVESTMENT_GRADE = 15 | SPECULATIVE/UNKNOWN = 25 |
| payment_history_indicator | STRONG = 5 | AVERAGE = 15 | WEAK/UNKNOWN = 25 |
| buyer_financial_stability | STABLE = 5 | MODERATE = 15 | UNCERTAIN = 25 |

Sum all four factors. Total is the `buyer_risk_score` (max 100).

**Buyer risk tier:**
- LOW RISK: 0–30
- MODERATE RISK: 31–55
- HIGH RISK: 56–100

**Variables to Extract:**
- buyer_risk_score
- buyer_risk_tier

**Expected Output:**
```json
{
  "buyer_risk_result": {
    "buyer_risk_score": 20,
    "buyer_risk_tier": "LOW RISK",
    "score_breakdown": {
      "buyer_size": 5,
      "credit_rating": 5,
      "payment_history": 5,
      "financial_stability": 5
    },
    "summary": "Global Motors Corp is a large, financially stable enterprise with investment-grade credit quality. Payment risk is low."
  }
}
```

**Verification:**
- `buyer_risk_score` must equal the sum of the four breakdown components
- `buyer_risk_tier` must match the score band
- `summary` must be at least 1 sentence

## Final Output Format
A `buyer_risk_result` with score, tier, and summary passed into the pipeline luggage.

## Success Criteria
1. All four buyer risk factors are assessed with clear rationale
2. Score arithmetic is correct
3. Risk tier correctly reflects the score band
