# Skill Name: Financial Statement Analysis with Flux Analysis

## Metadata
- Version: 1.0.0
- Author: SkillEngine Team
- Description: Analyzes financial statements for GAAP compliance, calculates period-over-period variances, and generates professional flux analysis reports with materiality-based variance commentary
- Tags: finance, financial-statements, flux-analysis, variance-analysis, GAAP, reporting

## Context

This skill automates the process of performing comprehensive financial statement analysis with period-over-period flux analysis. It assists finance teams with:

**Purpose:** Flux analysis (variance analysis) is a critical component of financial reporting, helping organizations understand period-over-period changes, identify trends, and communicate financial performance to stakeholders.

**GAAP Framework:** This skill evaluates financial statements against Generally Accepted Accounting Principles (GAAP) presentation requirements:
- **ASC 220 (Income Statement):** Requires presentation of all items of income and expense, proper classification of operating vs. non-operating items, and separate disclosure of income tax expense. Expenses should be classified by function (COGS, R&D, S&M, G&A) with required note disclosures.
- **ASC 210 (Balance Sheet):** Requires distinction between current and non-current assets/liabilities based on 12-month realiz ability. Assets presented in liquidity order, receivables net of allowances, and proper classification of lease assets/liabilities.
- **ASC 230 (Cash Flow Statement):** Requires categorization of cash flows into operating, investing, and financing activities. Most companies use the indirect method starting with net income.

**Variance Analysis Methodology:** The skill applies structured variance analysis:
1. Calculate dollar and percentage variances for all line items
2. Apply materiality thresholds to identify significant variances requiring investigation
3. Decompose variances into drivers (volume, rate, mix, timing, one-time items)
4. Provide narrative business explanations for material variances
5. Assess whether variances represent trends or are temporary

**Period-End Context:** Financial statements reflect period-end adjustments including accruals, deferrals, depreciation/amortization, bad debt provisions, inventory adjustments, FX revaluations, and tax provisions. Common reclassifications include current/non-current shifts, contra account netting, intercompany eliminations, and segment classifications.

**Important Disclaimer:** This skill assists with financial statement workflows but does not provide financial advice. All statements and analysis should be reviewed by qualified financial professionals before use in reporting, filings, or decision-making.

## Reference Files
- examples/sample_data/financial_statement.txt


## Steps

### Step 1: Extract and Validate Financial Data

**Instruction:**

Extract all line items from the provided current period and prior period financial statements. Organize the data into three statement categories: Income Statement, Balance Sheet, and Cash Flow Statement (if available).

For each statement, extract:

**Income Statement Items:**
- Revenue (by category if disaggregated: product, service, other)
- Cost of Revenue/COGS (by category if available)
- Gross Profit
- Operating Expenses (R&D, Sales & Marketing, G&A, each separately)
- Operating Income
- Other Income/Expense (Interest income, Interest expense, Other)
- Income Before Taxes
- Income Tax Expense
- Net Income
- EPS if present (Basic and Diluted)

**Balance Sheet Items:**
- Current Assets (Cash, Short-term investments, AR net, Inventory, Prepaid, Other)
- Non-Current Assets (PP&E net, ROU assets, Goodwill, Intangibles net, LT investments, Other)
- Total Assets
- Current Liabilities (AP, Accrued liabilities, Deferred revenue current, Current debt, Current lease liabilities, Other)
- Non-Current Liabilities (Long-term debt, Deferred revenue LT, LT lease liabilities, Other)
- Total Liabilities
- Stockholders' Equity (Common stock, APIC, Retained earnings, AOCI, Treasury stock)
- Total Equity

**Cash Flow Statement Items (if available):**
- Operating Activities (starting with Net Income, all adjustments and changes in working capital)
- Investing Activities (all categories)
- Financing Activities (all categories)
- Net Change in Cash

**Validation Requirements:**
1. Verify Balance Sheet equation: Total Assets = Total Liabilities + Total Equity (both periods)
2. Verify Income Statement: Gross Profit = Revenue - COGS
3. Verify Income Statement: Operating Income = Gross Profit - Operating Expenses
4. Check that all major line items are present
5. Confirm company name and reporting period are identified for both periods

Present extracted data in structured JSON format with clear labels for both current and prior periods.

**Reference Files:**
- examples/sample_data/financial_statement.txt

**Expected Output:**

JSON format containing:
```json
{
  "company_name": "Company Name",
  "current_period": "Period description",
  "prior_period": "Period description",
  "income_statement": {
    "current": { "revenue": 0, "cogs": 0, ... },
    "prior": { "revenue": 0, "cogs": 0, ... }
  },
  "balance_sheet": {
    "current": { "total_assets": 0, "total_liabilities": 0, ... },
    "prior": { "total_assets": 0, "total_liabilities": 0, ... }
  },
  "cash_flow_statement": {
    "current": { "operating_activities": 0, ... },
    "prior": { "operating_activities": 0, ... }
  },
  "validation_results": {
    "balance_sheet_balances": true,
    "income_statement_calcs_correct": true,
    "all_major_items_present": true
  }
}
```

**Verification:**
- Must contain both current and prior period data
- Must include Income Statement and Balance Sheet as minimum (Cash Flow optional)
- Balance Sheet must balance for both periods (Assets = Liabilities + Equity, within $1 rounding tolerance)
- Must include company name and reporting periods
- All extracted numeric values must be in dollars (no text in numeric fields)
- Validation results must show all checks passed

### Step 2: Calculate Period-over-Period Variances

**Instruction:**

For each line item extracted in Step 1, calculate comprehensive period-over-period variances. Use the following calculation methodology:

**Variance Calculations:**
1. **Dollar Variance:** Current Period - Prior Period
   - Positive value indicates increase
   - Negative value indicates decrease

2. **Percentage Variance:** ((Current - Prior) / |Prior|) × 100
   - Handle special cases:
     - If Prior = 0 and Current > 0: Show as "N/A - New item" or "∞"
     - If Prior = 0 and Current = 0: Show as "0%"
     - If Prior < 0 and Current > 0: Note as "Swing from loss to profit" (or similar)
     - Use absolute value of Prior in denominator for consistency

3. **Favorable/Unfavorable Classification:**
   - **Income Statement:**
     - Revenue increase = Favorable
     - Expense increase = Unfavorable
     - Loss reduction = Favorable
   - **Balance Sheet:**
     - Asset increase = Neutral (provide context)
     - Liability increase = Unfavorable (generally)
     - Equity increase = Favorable

4. **Key Financial Ratios (calculate for both periods):**
   - Gross Profit Margin = (Revenue - COGS) / Revenue × 100
   - Operating Margin = Operating Income / Revenue × 100
   - Net Profit Margin = Net Income / Revenue × 100
   - Return on Assets (ROA) = Net Income / Avg Total Assets × 100
   - Current Ratio = Current Assets / Current Liabilities
   - Debt-to-Equity = Total Liabilities / Total Equity

5. **Basis Point Changes for Margins:**
   - Calculate: (Current Margin % - Prior Margin %) × 100
   - Example: If margin went from 45.2% to 47.8%, change is +260 basis points

Present all calculations in organized tables with clear headers and proper formatting.

**Expected Output:**

Comprehensive variance analysis tables showing:

**Income Statement Variance Table:**
| Line Item | Prior Period ($) | Current Period ($) | $ Variance | % Variance | F/U |
|-----------|-----------------|-------------------|------------|------------|-----|
| Revenue | X | Y | Y-X | % | F/U |
| COGS | X | Y | Y-X | % | F/U |
| ... | ... | ... | ... | ... | ... |

**Balance Sheet Variance Table:**
| Line Item | Prior Period ($) | Current Period ($) | $ Variance | % Variance | Notes |
|-----------|-----------------|-------------------|------------|------------|-------|
| Cash | X | Y | Y-X | % | Context |
| ... | ... | ... | ... | ... | ... |

**Key Ratios Comparison:**
| Ratio | Prior Period | Current Period | Change | Basis Points |
|-------|--------------|----------------|---------|--------------|
| Gross Margin | X% | Y% | +/- Z% | +/- BP |
| ... | ... | ... | ... | ... |

**Verification:**
- Must include variances for all major line items from Step 1
- All variance calculations must be mathematically correct
- Must classify Income Statement variances as Favorable or Unfavorable
- Must handle zero or negative prior period amounts appropriately (show N/A or special notation)
- Must calculate all 6 key financial ratios for both periods
- Basis point changes for margin ratios must be included

### Step 3: Assess Materiality and Identify Key Variances

**Instruction:**

Apply materiality thresholds to the variances calculated in Step 2 to identify which variances require detailed investigation and commentary. Use a combined threshold approach where a variance is considered material if it meets EITHER the dollar threshold OR the percentage threshold.

**Materiality Thresholds:**

**Income Statement Items:**
- Dollar Threshold: >$100,000
- Percentage Threshold: >10%
- Combined Logic: Flag if ($Variance > $100K) OR (|%Variance| > 10%)

**Balance Sheet Items:**
- Dollar Threshold: >$250,000
- Percentage Threshold: >15%
- Combined Logic: Flag if ($Variance > $250K) OR (|%Variance| > 15%)

**Special Considerations:**
- High-volatility items may warrant higher thresholds (e.g., Other Income/Expense)
- Critical items may warrant lower thresholds (e.g., Cash, Debt)
- Zero-to-value or value-to-zero changes are automatically material

**Process:**
1. Apply thresholds to all line items
2. Flag items that exceed either threshold
3. Rank material variances by absolute dollar magnitude
4. Identify the top 10 material variances requiring detailed commentary
5. Note any items just below thresholds that warrant monitoring

**Expected Output:**

**Material Variances Summary:**
| Rank | Line Item | Statement | $ Variance | % Variance | Materiality Flag | Priority |
|------|-----------|-----------|------------|------------|-----------------|----------|
| 1 | [Item] | IS/BS/CF | $X | Y% | $ and % | High |
| 2 | [Item] | IS/BS/CF | $X | Y% | $ or % | High |
| ... | ... | ... | ... | ... | ... | ... |
| 10 | [Item] | IS/BS/CF | $X | Y% | $ or % | High |

**Items Below Threshold (Monitor):**
- List items between 75-100% of thresholds

**Materiality Assessment Summary:**
- Total material variances identified: [N]
- Income Statement material items: [N]
- Balance Sheet material items: [N]
- Top 10 variances represent $X of total variance ($Y)

**Verification:**
- Must identify material variances (minimum 5 if they exist in the data)
- Must include priority ranking (1-10 for top items)
- Materiality thresholds must be clearly stated in output
- All flagged items must actually exceed at least one threshold
- Must show WHY each item is material (which threshold it exceeded)

### Step 4: Perform Variance Decomposition Analysis

**Instruction:**

For each of the top 10 material variances identified in Step 3, perform detailed root cause analysis using variance decomposition methodology. The goal is to explain WHY each variance occurred and whether it represents a sustainable trend or a one-time event.

**Variance Decomposition Framework:**

For each material variance, analyze using these driver categories:

1. **Volume/Quantity Effect:** Change driven by changes in volume, units sold, headcount, or activity levels
   - Example: Revenue increased due to 15% unit volume growth
   - Quantify: Isolate the impact of volume change at prior period rates

2. **Rate/Price Effect:** Change driven by changes in prices, rates, or per-unit costs
   - Example: Avg selling price increased from $50 to $55 per unit
   - Quantify: Isolate the impact of rate change at current period volumes

3. **Mix Effect:** Change driven by shifts in product/customer/channel mix
   - Example: Higher mix of premium products (70% vs 60% prior period)
   - Quantify: Impact of composition shift between items with different margins

4. **New/Discontinued Items:** Items present in one period but not the other
   - Example: Launched new product line generating $2M revenue
   - Quantify: Full amount attributable to new/discontinued items

5. **One-Time/Non-Recurring Items:** Items not expected to repeat
   - Example: $500K restructuring charge, $1M insurance recovery
   - Quantify: Identify and isolate non-recurring amounts

6. **Timing Effect:** Items shifting between periods without changing run rate
   - Example: Invoice timing caused Q4 expense to shift to Q1
   - Quantify: Amount that shifted due to timing

7. **Currency Effect (if applicable):** Impact of foreign exchange rate changes
   - Example: Unfavorable FX impact of $200K due to EUR/USD movement
   - Quantify: Translate at constant FX rates to isolate impact

**Analysis Requirements:**
For EACH of the top 10 variances, provide:
- Variance description (line item, amount, %)
- Primary driver category (which of the 7 categories above)
- Quantified impact breakdown (how much of variance explained by each driver)
- Narrative business explanation (why did this happen in business terms)
- Trend vs. One-Time assessment (is this a new run rate or temporary?)
- Management action/implication (what should be done about it)

**Expected Output:**

**Detailed Variance Analysis (for each of top 10):**

**Variance #1: [Line Item Name]**
- **Amount:** $X variance (Y% change)
- **Classification:** Favorable/Unfavorable
- **Primary Driver:** [Category name]
- **Decomposition:**
  - Volume effect: $X
  - Rate effect: $Y
  - Mix effect: $Z
  - One-time items: $W
  - Other: $V
  - Total explained: $X (should match variance)
- **Business Explanation:** [2-3 sentence narrative explaining WHY this occurred in business context - reference specific business events, market conditions, management actions, etc.]
- **Trend Assessment:** ☐ Represents new run rate ☐ Temporary/One-time ☐ Mixed
- **Implication:** [What this means for future periods and any actions required]

[Repeat for all top 10 variances]

**Verification:**
- Must analyze all top 10 material variances identified in Step 3
- Each variance must have a primary driver category identified
- Decomposition should be quantified (even if approximate)
- Must include narrative business reasoning for each variance
- Must assess whether each variance is a trend or one-time occurrence
- Decomposition amounts should approximately sum to total variance

### Step 5: Assess GAAP Presentation Compliance

**Instruction:**

Review the financial statements from Step 1 against GAAP presentation requirements to identify any compliance issues, presentation concerns, or areas requiring note disclosure. Reference specific Accounting Standards Codification (ASC) guidance.

**GAAP Presentation Checklist:**

**Income Statement (ASC 220):**
☐ All items of income and expense for the period are presented
☐ Revenue is properly disaggregated showing nature, amount, timing per ASC 606
☐ Expenses are classified by function (COGS, R&D, S&M, G&A)
☐ If functional classification used, depreciation and employee benefits disclosed in notes
☐ Operating and non-operating items are clearly separated
☐ Income tax expense shown as separate line item
☐ No extraordinary items presented (prohibited under GAAP)
☐ Discontinued operations (if any) presented separately, net of tax
☐ EPS presented with both basic and diluted (if applicable)

**Income Statement Presentation Considerations:**
- Stock-based compensation properly classified within functional expenses
- Restructuring charges separately disclosed if material
- Non-GAAP measures clearly labeled and reconciled (if presented in external reports)

**Balance Sheet (ASC 210):**
☐ Current and non-current assets/liabilities distinguished
☐ Current assets/liabilities: items expected to be realized/settled within 12 months
☐ Assets presented in order of liquidity
☐ Accounts receivable shown net of allowance for credit losses (ASC 326)
☐ Property and equipment shown net of accumulated depreciation
☐ Goodwill separately stated (not amortized, tested for impairment per ASC 350)
☐ Operating lease ROU assets and liabilities presented per ASC 842
☐ Deferred revenue properly classified between current and non-current
☐ Debt properly classified between current portion and long-term
☐ Treasury stock shown as reduction of equity (if applicable)

**Cash Flow Statement (ASC 230) - If Provided:**
☐ Cash flows classified into Operating, Investing, Financing activities
☐ Indirect method: starts with net income, adjusts for non-cash items
☐ Stock-based compensation added back in operating activities
☐ Depreciation and amortization added back in operating activities
☐ Changes in working capital accounts properly reflected
☐ Interest paid and taxes paid disclosed (face or notes)
☐ Non-cash investing/financing activities disclosed separately
☐ Cash equivalents defined (typically investments with maturities ≤ 3 months)

**Common Issues to Flag:**
- Improper current/non-current classification
- Missing required disaggregation
- Contra accounts not netted properly
- Lease accounting not reflecting ASC 842
- Revenue recognition not aligned with ASC 606
- Credit losses not following ASC 326 (CECL model)

**Expected Output:**

**GAAP Compliance Assessment Report:**

**Income Statement Compliance:**
- Checklist results: [X of Y items compliant]
- Issues identified:
  1. [Issue description] - Reference: ASC XXX - Recommendation: [How to fix]
  2. ...
- Items in compliance: [List key items done correctly]

**Balance Sheet Compliance:**
- Checklist results: [X of Y items compliant]
- Issues identified:
  1. [Issue description] - Reference: ASC XXX - Recommendation: [How to fix]
  2. ...
- Items in compliance: [List key items done correctly]

**Cash Flow Statement Compliance (if provided):**
- Checklist results: [X of Y items compliant]
- Issues identified: [List with ASC references]
- Items in compliance: [List key items done correctly]

**Overall Compliance Summary:**
- Overall assessment: ☐ Compliant ☐ Minor issues ☐ Material issues
- Priority corrections needed: [List]
- Note disclosures required: [List]

**Verification:**
- Must review all three statement types (or all that were provided)
- Must reference specific ASC guidance for any issues identified
- Must clearly state whether each requirement is compliant or non-compliant
- Recommendations must be specific and actionable
- Must distinguish between presentation issues and disclosure issues

### Step 6: Generate Flux Analysis Report

**Instruction:**

Synthesize all analysis from Steps 1-5 into a comprehensive, executive-ready flux analysis report. The report should communicate the financial story clearly to CFOs, controllers, board members, and other senior stakeholders.

**Report Structure:**

**1. EXECUTIVE SUMMARY** (0.5 pages)
- Company name and comparison periods
- Overall financial performance headline (revenue, income, key metrics)
- Top 3-5 key highlights/themes from the analysis
- Major drivers of performance
- Critical issues or concerns (if any)
- One-sentence bottom line assessment

**2. FINANCIAL PERFORMANCE OVERVIEW** (0.5 pages)
- High-level summary tables:
  - Income Statement: Revenue, Gross Profit, Operating Income, Net Income (current, prior, variance)
  - Balance Sheet: Total Assets, Total Liabilities, Total Equity (current, prior, variance)
  - Key Ratios: Gross Margin, Operating Margin, Net Margin, Current Ratio, D/E Ratio
- Notable trends visible in the summary metrics

**3. VARIANCE ANALYSIS BY STATEMENT** (1-1.5 pages)

**Income Statement Analysis:**
- Revenue performance and drivers
- Gross profit and margin trends
- Operating expense trends by category
- Below-the-line items (other income/expense, tax)
- Net income performance

**Balance Sheet Analysis:**
- Working capital changes and trends
- Asset composition changes
- Liability and debt movements
- Equity movements (retained earnings, other)

**Cash Flow Analysis (if provided):**
- Operating cash flow performance
- Key investing activities
- Key financing activities
- Overall liquidity position

**4. TOP 10 MATERIAL VARIANCES** (1.5-2 pages)
- Detailed commentary for each of the top 10 material variances identified in Step 3 and analyzed in Step 4
- For each variance include:
  - What: Line item, amount, percentage
  - Why: Business explanation from Step 4 analysis
  - Drivers: Decomposition summary
  - Outlook: Trend vs. one-time assessment
- Present in priority order (largest dollar impact first)

**5. GAAP COMPLIANCE SUMMARY** (0.25 pages)
- Overall compliance assessment from Step 5
- Any material presentation issues requiring correction
- Note disclosure requirements
- Brief statement on adherence to ASC guidance

**6. APPENDICES**
**Appendix A: Complete Variance Tables**
- Full Income Statement variance table
- Full Balance Sheet variance table
- Full Cash Flow variance table (if applicable)

**Appendix B: Methodology and Assumptions**
- Materiality thresholds used
- Variance calculation approach
- Key assumptions made in analysis
- Data sources

**Formatting Guidelines:**
- Use clear section headers and subsection headers
- Present financial data in well-formatted tables
- Use bullet points for readability
- Highlight key numbers (bold important variances)
- Keep business language clear (avoid excessive jargon)
- Target 3-5 pages total length

**Expected Output:**

A complete, professionally formatted flux analysis report following the structure above. The report should be suitable for presentation to executive management or a board of directors without further editing.

**Verification:**
- Must contain all 6 required sections (Executive Summary through Appendices)
- Must include detailed commentary on the top 10 material variances from Step 4
- Must be professionally formatted with clear headers and organized structure
- Must synthesize data and findings from ALL previous steps (1-5)
- Must be internally consistent (numbers should match across sections)
- Must be written in professional business language
- Should be 3-5 pages in length when formatted

## Final Output Format

The final output is a comprehensive flux analysis report suitable for presentation to executive management or a board of directors. The report should be 3-5 pages in professional business format with:

- Clear section headers and logical information flow
- Organized variance tables with proper formatting
- Narrative commentary in clear business language (avoiding excessive accounting jargon)
- Key trends and performance drivers prominently highlighted
- GAAP compliance concerns noted and explained
- Materiality thresholds and methodology documented in appendix

The report enables financial leaders to quickly understand period-over-period changes, identify key business drivers, and effectively communicate performance to stakeholders.

## Success Criteria

The skill is successful when:

1. **Data Accuracy:** All financial data is accurately extracted and validated from source documents with balance sheet balancing and math checks passing
2. **Calculation Accuracy:** All variance calculations (dollar, percentage, basis points) are mathematically correct and properly classified as favorable/unfavorable
3. **Materiality Assessment:** Appropriate materiality thresholds are consistently applied and material variances are correctly identified and ranked
4. **Root Cause Analysis:** Each of the top 10 material variances has a clear, logical driver analysis with quantified decomposition and business reasoning
5. **GAAP Compliance:** Financial statement presentation compliance is thoroughly assessed against relevant ASC guidance with specific issues and recommendations provided
6. **Report Quality:** Final flux analysis report is complete, comprehensive, professionally formatted, well-organized, and immediately actionable for executive stakeholders
7. **Verification Passed:** All step verification checks pass successfully
8. **Internal Consistency:** All analysis and conclusions are internally consistent across sections, with numbers matching throughout the report and findings aligned with data
