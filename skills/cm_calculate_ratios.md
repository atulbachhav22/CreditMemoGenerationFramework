# Skill Name: CM Step 2 - Calculate Financial Ratios

## Metadata
- Version: 1.0.0
- Author: SkillEngine Team
- Description: Calculates financial ratios from extracted data. Second step of the credit memo pipeline.
- Tags: finance, credit, ratios

## Context
This skill is the second step of the credit memo pipeline. The previous step (cm_extract_data) has already extracted all financial figures from the statement. Those results are available in the variable `cm_extract_data_output` in the current context.

Use the financial data from `cm_extract_data_output` to calculate all required ratios.

## Steps

### Step 1: Calculate Financial Ratios

**Instruction:**
The financial data extracted in the previous pipeline step is available in your context as the variable `cm_extract_data_output`. Using those figures, calculate the following financial ratios:

1. **Profitability Ratios:**
   - Gross Profit Margin = (Revenue - COGS) / Revenue × 100
   - Operating Profit Margin = (Revenue - COGS - Operating Expenses) / Revenue × 100
   - Net Profit Margin = Net Income / Revenue × 100
   - Return on Assets (ROA) = Net Income / Total Assets × 100
   - Return on Equity (ROE) = Net Income / Shareholders' Equity × 100

2. **Liquidity Ratios:**
   - Current Ratio = Current Assets / Current Liabilities
   - Quick Ratio = (Current Assets - Inventory) / Current Liabilities
   - Cash Ratio = Cash and Cash Equivalents / Current Liabilities

3. **Leverage Ratios:**
   - Debt-to-Equity Ratio = Total Liabilities / Shareholders' Equity
   - Debt-to-Assets Ratio = Total Liabilities / Total Assets × 100

Present all ratios with clear labels and appropriate formatting (percentages or decimals).

**Expected Output:**
Structured format showing all 10 calculated ratios grouped by category (Profitability, Liquidity, Leverage). Include the formula and computed value for each ratio.

**Verification:**
- Must contain all 10 financial ratios
- All calculations must be mathematically correct based on the extracted data
- Ratios must be presented with appropriate units (%, decimal)
- Each ratio must include its name and value

## Final Output Format
Structured report of all financial ratios grouped by category.

## Success Criteria
All 10 ratios are calculated correctly using the data from the previous pipeline step.
