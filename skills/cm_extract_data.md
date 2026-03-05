# Skill Name: CM Step 1 - Extract Financial Data

## Metadata
- Version: 1.0.0
- Author: SkillEngine Team
- Description: Extracts key financial figures from a financial statement. First step of the credit memo pipeline.
- Tags: finance, credit, extraction

## Context
This skill is the first step of the credit memo pipeline. It reads the provided financial statement and extracts all key figures needed for subsequent analysis steps.

## Reference Files
- examples/sample_data/financial_statement.txt

## Steps

### Step 1: Extract Financial Data

**Instruction:**
Extract all key financial figures from the provided financial statement. You must identify and extract the following:

- Company Name
- Reporting Period
- Total Revenue
- Cost of Goods Sold (COGS)
- Operating Expenses
- Net Income
- Total Assets
- Current Assets
- Total Liabilities
- Current Liabilities
- Shareholders' Equity
- Cash and Cash Equivalents

Present the extracted data in a structured JSON format with clear labels.

**Reference Files:**
- examples/sample_data/financial_statement.txt

**Expected Output:**
JSON format with all required financial fields. Each field should have a numeric value (in dollars) and the field name should match exactly as listed above.

**Verification:**
- Must contain all 12 required financial fields
- All values must be numeric (dollars)
- Company name must be extracted
- Reporting period must be identified
- Total Assets must equal Total Liabilities plus Shareholders' Equity (basic accounting equation)

## Final Output Format
JSON object containing all extracted financial fields with their values.

## Success Criteria
All 12 financial fields are extracted accurately from the source document.
