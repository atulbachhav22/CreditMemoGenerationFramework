# Skill Name: Credit Memo Generation

## Metadata
- Version: 1.0.0
- Author: SkillEngine Team
- Description: Generates professional credit memos from financial analysis data
- Tags: finance, credit, memo, reporting

## Context
This skill takes the output from the Financial Analysis skill and transforms it into a professional, actionable credit memo. It synthesizes financial data, ratios, and risk assessment into a comprehensive document suitable for credit committee review.

The skill expects pre-processed financial analysis data as input and produces a formatted credit memo with clear recommendations.

## Steps

### Step 1: Prepare Analysis Data

**Instruction:**
You will receive financial analysis data from the previous skill. This data includes:
- Extracted financial metrics
- Calculated financial ratios
- Risk assessment and rating

Extract and organize this data for use in memo generation. If the data is provided in the input variables under "skill_1_output", parse and structure it appropriately.

**Expected Output:**
Well-organized analysis data ready for memo composition.

**Verification:**
- Input data must contain financial figures
- Input data must contain calculated ratios
- Input data must contain risk assessment with a rating

### Step 2: Generate Credit Memo

**Instruction:**
Create a comprehensive, professional credit memo that synthesizes all provided financial analysis. The credit memo should be formatted for presentation to a credit committee or lending officer.

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
   - Key financial figures from the analysis
   - Notable trends or concerns

4. **Financial Ratio Analysis**
   - Summary of key ratios
   - Highlight strongest and weakest metrics

5. **Credit Risk Assessment**
   - Risk rating and justification
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
- Must reference specific data from the financial analysis
- Must be professionally formatted and free of errors
- Recommendation must be consistent with the risk assessment provided

### Step 3: Add Analyst Information

**Instruction:**
Add analyst metadata to the credit memo including:
- Analyst Name (from variable: analyst_name)
- Analysis Date (from variable: date, or current date if not provided)
- Memo ID/Reference Number

This information should be added to the memo header or footer for tracking purposes.

**Expected Output:**
Final credit memo with complete analyst metadata.

**Verification:**
- Analyst name must be included
- Date must be included
- Memo should be ready for distribution

## Final Output Format
The final output should be a complete credit memo document that could be presented to a credit committee. It should be formatted in professional business style with clear section headers, proper grammar, and logical flow.

## Success Criteria
The skill is considered successful when:
1. The input financial analysis data is properly parsed
2. All 7 required sections are included in the memo
3. The memo is professional and actionable
4. Credit recommendation aligns with the risk assessment
5. All verification checks pass
6. Analyst information is included