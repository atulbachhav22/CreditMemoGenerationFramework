# Skill Name: CM Step 4 - Generate Credit Memo

## Metadata
- Version: 1.0.0
- Author: SkillEngine Team
- Description: Generates the final credit memo from all previous pipeline outputs. Fourth step of the credit memo pipeline.
- Tags: finance, credit, document-generation

## Context
This skill is the final step of the credit memo pipeline. All prior analysis is available in context:
- `cm_extract_data_output`: Raw financial figures
- `cm_calculate_ratios_output`: All calculated financial ratios
- `cm_risk_assessment_output`: Credit risk assessment with overall risk rating

Synthesize all three into a professional credit memo document.

## Steps

### Step 1: Generate Credit Memo

**Instruction:**
The full analysis from the previous pipeline steps is available in your context:
- `cm_extract_data_output` — extracted financial figures
- `cm_calculate_ratios_output` — calculated financial ratios
- `cm_risk_assessment_output` — risk assessment and overall risk rating

Using all of this information, create a comprehensive, professional credit memo structured as follows:

1. **Executive Summary**
   - Company name and reporting period
   - Recommended credit decision (Approve / Approve with Conditions / Decline)
   - Credit limit recommendation (if applicable)
   - Brief overview of key findings

2. **Company Overview**
   - Basic information from the financial statement

3. **Financial Performance Summary**
   - Key financial figures from the extraction step
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
- Must include a clear credit decision (Approve / Approve with Conditions / Decline)
- Must reference specific data from all three previous pipeline steps
- Must be professionally formatted and free of errors
- Recommendation must be consistent with the risk rating

## Final Output Format
A complete credit memo document formatted for presentation to a credit committee or lending officer.

## Success Criteria
The credit memo is complete, professionally formatted, includes all 7 sections, and the recommendation is consistent with the risk assessment.
