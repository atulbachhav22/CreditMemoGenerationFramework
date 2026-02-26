# Skill Name: Financial Analysis

## Metadata
- Version: 1.0.0
- Author: SkillEngine Team
- Description: Analyzes financial statements, extracts metrics, calculates ratios, and performs credit risk assessment
- Tags: finance, analysis, risk-assessment, financial-metrics

## Context
This skill automates the extraction and analysis of financial data from financial statements. It extracts key financial metrics, performs comprehensive ratio analysis, and conducts credit risk assessment following industry best practices.

The process follows these steps:
1. Extract and validate financial data
2. Calculate key financial ratios (profitability, liquidity, leverage)
3. Assess credit risk based on multiple factors
4. Produce structured analysis output for downstream processing

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

### Step 2: Calculate Financial Ratios

**Instruction:**
Based on the financial data extracted in Step 1, calculate the following financial ratios:

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
Structured format showing all calculated ratios grouped by category (Profitability, Liquidity, Leverage). Include the formula used for each ratio.

**Verification:**
- Must contain all 10 financial ratios
- All calculations must be mathematically correct based on Step 1 data
- Ratios must be presented with appropriate units (%, decimal)
- Each ratio must include its name and value

### Step 3: Perform Credit Risk Assessment

**Instruction:**
Conduct a comprehensive credit risk assessment based on the financial data and ratios from previous steps. Analyze the following risk factors:

1. **Profitability Analysis:**
   - Evaluate profit margins (are they healthy for the industry?)
   - Assess ROA and ROE (strong, moderate, or weak returns?)

2. **Liquidity Analysis:**
   - Current Ratio assessment (>2.0 = Strong, 1.0-2.0 = Moderate, <1.0 = Weak)
   - Quick Ratio assessment (>1.0 = Strong, 0.5-1.0 = Moderate, <0.5 = Weak)
   - Cash position relative to current liabilities

3. **Leverage Analysis:**
   - Debt-to-Equity ratio (>2.0 = High Risk, 1.0-2.0 = Moderate, <1.0 = Low Risk)
   - Debt-to-Assets percentage (>60% = High Risk, 40-60% = Moderate, <40% = Low Risk)

4. **Overall Risk Rating:**
   Based on the above analysis, assign an overall risk rating:
   - LOW RISK: Strong financials across all categories
   - MODERATE RISK: Mixed indicators with some concerns
   - HIGH RISK: Weak financials or red flags in multiple areas

Provide a detailed narrative explanation of your assessment with specific references to the calculated metrics.

**Expected Output:**
A structured risk assessment report with:
- Analysis of each category (Profitability, Liquidity, Leverage)
- Specific commentary on each key ratio
- Overall risk rating (LOW, MODERATE, or HIGH RISK)
- Key risk factors identified
- Key strengths identified

**Verification:**
- Must provide analysis for all three categories (Profitability, Liquidity, Leverage)
- Must assign an overall risk rating (LOW, MODERATE, or HIGH RISK)
- Must reference specific ratios and metrics from Step 2
- Analysis must be logical and consistent with the data

## Final Output Format
The final output should be a comprehensive JSON or structured format containing:
```json
{
  "financial_data": { /* extracted financial figures */ },
  "financial_ratios": { /* calculated ratios */ },
  "risk_assessment": { /* risk analysis and rating */ }
}
```

## Success Criteria
The skill is considered successful when:
1. All financial data is accurately extracted from the source document
2. All financial ratios are calculated correctly
3. The risk assessment is thorough and logically sound
4. All verification checks pass for each step
5. Output is in structured format for downstream processing