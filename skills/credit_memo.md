# Skill Name: Credit Memo Generator

## Metadata
- Version: 1.0.0
- Author: SkillEngine Team
- Description: Analyzes financial statements and generates comprehensive credit memos with risk assessment
- Tags: finance, credit, risk-analysis, financial-analysis

## Context
This skill automates the process of generating credit memos from financial statements. It extracts key financial metrics, performs risk analysis, calculates credit scores, and produces a structured credit memo suitable for lending decisions.

The process follows industry best practices for credit evaluation:
1. Extract and validate financial data
2. Calculate key financial ratios
3. Assess credit risk based on multiple factors
4. Generate final credit memo with recommendations

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
- Overall risk rating (LOW, MODERATE, or HIGH)
- Key risk factors identified
- Key strengths identified

**Verification:**
- Must provide analysis for all three categories (Profitability, Liquidity, Leverage)
- Must assign an overall risk rating (LOW, MODERATE, or HIGH RISK)
- Must reference specific ratios and metrics from Step 2
- Analysis must be logical and consistent with the data

### Step 4: Generate Credit Memo

**Instruction:**
Create a comprehensive, professional credit memo that synthesizes all previous analysis. The credit memo should be formatted for presentation to a credit committee or lending officer.

Structure the credit memo with the following sections:

1. **Executive Summary**
   - Company name and reporting period
   - Recommended credit decision (Approve/Approve with Conditions/Decline)
   - Credit limit recommendation (if applicable)
   - Brief overview of key findings

2. **Company Overview**
   - Basic information from the financial statement
   - Nature of business (if mentioned)

3. **Financial Performance Summary**
   - Key financial figures from Step 1
   - Notable trends or concerns

4. **Financial Ratio Analysis**
   - Summary of key ratios from Step 2
   - Highlight strongest and weakest metrics

5. **Credit Risk Assessment**
   - Risk rating and justification from Step 3
   - Key risk factors
   - Mitigating factors

6. **Recommendation**
   - Clear credit decision
   - Recommended credit limit (if approving)
   - Suggested terms and conditions
   - Monitoring requirements

7. **Appendix**
   - Complete list of financial data
   - Complete list of calculated ratios

The memo should be professional, concise, and actionable.

**Expected Output:**
A complete, well-formatted credit memo in professional business format. Should be 2-4 pages in length when printed.

**Verification:**
- Must contain all 7 required sections
- Must include a clear credit decision (Approve/Approve with Conditions/Decline)
- Must reference specific data from previous steps
- Must be professionally formatted and free of errors
- Recommendation must be consistent with the risk assessment from Step 3

## Final Output Format
The final output should be a complete credit memo document that could be presented to a credit committee. It should be formatted in professional business style with clear section headers, proper grammar, and logical flow.

## Success Criteria
The skill is considered successful when:
1. All financial data is accurately extracted from the source document
2. All financial ratios are calculated correctly
3. The risk assessment is thorough and logically sound
4. The final credit memo is complete, professional, and actionable
5. All verification checks pass for each step
6. The credit recommendation aligns with the risk assessment
