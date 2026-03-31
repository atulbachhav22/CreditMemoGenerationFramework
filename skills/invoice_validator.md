# Skill Name: Invoice Validator

## Metadata
- Version: 1.0.0
- Author: SkillEngine Team
- Description: Validates an invoice submitted for financing — extracts key fields and confirms the invoice is complete and eligible
- Tags: invoice, validation, trade-finance, factoring

## Context
This is the entry point of the Invoice Financing pipeline. A seller (supplier) has submitted an invoice issued to a buyer (customer) and is requesting early payment from the financier at a discount.

Before any credit analysis begins, the invoice itself must be validated:
1. Are all required fields present and consistent?
2. Is the invoice eligible for financing (not overdue, not already assigned)?

The outputs feed into two parallel downstream skills:
- `buyer_credit_check` — is the buyer likely to pay?
- `seller_health_check` — is the seller a financially healthy business?

## Steps

### Step 1: Extract Invoice Data

**Instruction:**
From the invoice data provided in the pipeline context, extract the following fields:

- `invoice_number` — unique invoice identifier
- `invoice_date` — date the invoice was issued (YYYY-MM-DD)
- `due_date` — payment due date (YYYY-MM-DD)
- `days_until_due` — number of days from today (2026-03-27) until due_date
- `seller_name` — name of the company that issued the invoice
- `buyer_name` — name of the company that owes payment
- `invoice_amount_usd` — total amount owed (USD)
- `currency` — invoice currency
- `description` — brief description of goods or services
- `payment_terms` — e.g. "Net 30", "Net 60"

If any field is missing, add it to `missing_fields`.

**Expected Output:**
```json
{
  "invoice_data": {
    "invoice_number": "INV-2026-00842",
    "invoice_date": "2026-03-01",
    "due_date": "2026-04-30",
    "days_until_due": 34,
    "seller_name": "Apex Components Ltd",
    "buyer_name": "Global Motors Corp",
    "invoice_amount_usd": 185000,
    "currency": "USD",
    "description": "Industrial hydraulic components — Purchase Order #PO-88821",
    "payment_terms": "Net 60"
  },
  "missing_fields": []
}
```

**Verification:**
- `invoice_number` must not be null
- `invoice_amount_usd` must be a positive number
- `days_until_due` must be a positive integer (negative = already overdue)
- `seller_name` and `buyer_name` must not be null

---

### Step 2: Check Invoice Eligibility

**Instruction:**
Using the extracted invoice data from Step 1, check whether the invoice is eligible for financing.

Apply these eligibility rules:

| Rule | Pass Condition |
|------|---------------|
| Not overdue | `days_until_due` > 0 |
| Minimum amount | `invoice_amount_usd` ≥ $10,000 |
| Maximum amount | `invoice_amount_usd` ≤ $5,000,000 |
| Minimum tenor | `days_until_due` ≥ 14 days |
| Maximum tenor | `days_until_due` ≤ 120 days |
| Supported currency | `currency` is USD, EUR, or GBP |

For each rule, record PASS or FAIL.

Overall `eligibility_status`:
- ELIGIBLE — all rules pass
- INELIGIBLE — one or more rules fail (halt the pipeline)

**Variables to Extract:**
- eligibility_status
- invoice_amount_usd
- buyer_name
- seller_name
- days_until_due

**Expected Output:**
```json
{
  "eligibility_check": {
    "not_overdue": "PASS",
    "minimum_amount": "PASS",
    "maximum_amount": "PASS",
    "minimum_tenor": "PASS",
    "maximum_tenor": "PASS",
    "supported_currency": "PASS",
    "eligibility_status": "ELIGIBLE",
    "failed_rules": []
  }
}
```

**Verification:**
- `eligibility_status` must be ELIGIBLE or INELIGIBLE
- If `eligibility_status` is INELIGIBLE, `failed_rules` must list the failing rules
- If INELIGIBLE, halt the pipeline

**Verification Settings:**
- Max Retries: 2
- Fail Action: halt

## Final Output Format
A validated invoice with `invoice_data` and `eligibility_check` passed into the pipeline luggage.

## Success Criteria
1. All invoice fields are extracted correctly
2. Every eligibility rule is evaluated
3. INELIGIBLE invoices halt the pipeline immediately with clear reasons
