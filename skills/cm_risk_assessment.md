# Skill Name: CM Step 3 - Credit Risk Assessment

## Metadata
- Version: 1.0.0
- Author: SkillEngine Team
- Description: Performs credit risk assessment from financial data and ratios. Third step of the credit memo pipeline.
- Tags: finance, credit, risk-analysis

## Context
This skill is the third step of the credit memo pipeline. The previous steps have produced:
- `cm_extract_data_output`: Raw financial figures extracted from the statement
- `cm_calculate_ratios_output`: All calculated financial ratios

Use both of these context variables to perform a thorough credit risk assessment.

## Steps

### Step 1: Perform Credit Risk Assessment

**Instruction:**
The financial figures and ratios from the previous pipeline steps are available in your context as `cm_extract_data_output` and `cm_calculate_ratios_output`. Using those results, conduct a comprehensive credit risk assessment covering the following areas:

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

Provide a detailed narrative explanation referencing specific metrics.

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
- Must reference specific ratios and metrics from the previous step
- Analysis must be logical and consistent with the data

## Final Output Format
Structured risk assessment report with category analyses, risk rating, key factors and strengths.

## Success Criteria
A thorough, logically sound risk assessment that references all key ratios and assigns a clear risk rating.
