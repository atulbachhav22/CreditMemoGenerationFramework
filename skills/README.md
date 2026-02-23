# Creating Skills for SkillEngine

This guide explains how to create skill definitions in Markdown format.

## Skill Structure

A skill is a Markdown file (`.md`) with the following structure:

```markdown
# Skill Name: [Your Skill Name]

## Metadata
[Skill metadata fields]

## Context
[Background information]

## Reference Files
[Global files available to all steps]

## Steps
[Step definitions]

## Final Output Format
[Description of final output]

## Success Criteria
[What makes this skill successful]
```

## Section Reference

### 1. Skill Name (Required)

The top-level heading defines the skill name:

```markdown
# Skill Name: Credit Memo Generator
```

Or simply:

```markdown
# Credit Memo Generator
```

### 2. Metadata (Optional but Recommended)

Metadata provides information about the skill:

```markdown
## Metadata
- Version: 1.0.0
- Author: John Doe
- Description: Generates credit memos from financial statements
- Tags: finance, credit, analysis
```

**Supported Fields:**
- `Version` - Semantic version (e.g., 1.0.0)
- `Author` - Creator's name
- `Description` - Brief description of what the skill does
- `Tags` - Comma-separated tags for categorization

### 3. Context (Optional)

General context that applies to the entire skill:

```markdown
## Context
This skill analyzes financial statements to generate comprehensive credit memos.
It follows industry best practices and regulatory guidelines...
```

This context is included in every LLM prompt to provide background.

### 4. Reference Files (Optional)

Files that are loaded once and available to all steps:

```markdown
## Reference Files
- data/guidelines.txt
- templates/memo_template.docx
- config/risk_thresholds.json
```

**Notes:**
- Paths can be relative (to the project root) or absolute
- Supported formats: TXT, PDF, DOCX, JSON, CSV, MD, XML, YAML
- Files are loaded into the luggage and accessible to all steps

### 5. Steps (Required)

Steps define the sequential workflow. Each step is a level-3 heading:

```markdown
## Steps

### Step 1: Extract Data

**Instruction:**
Extract all financial figures from the provided statement...

**Reference Files:**
- financial_statement.pdf

**Expected Output:**
JSON format with the following fields...

**Verification:**
- Must contain revenue field
- Must contain expenses field
- All values must be numeric
```

#### Step Components

##### Step Header (Required)
```markdown
### Step 1: Extract Data
```
Format: `### Step [number]: [name]`

##### Instruction (Required)
```markdown
**Instruction:**
What the LLM should do in this step...
```

The instruction is the core prompt for the LLM. Be clear and specific.

##### Description (Optional)
```markdown
**Description:**
Additional context about this step...
```

##### Reference Files (Optional)
```markdown
**Reference Files:**
- file1.txt
- file2.pdf
```

Files specific to this step (in addition to global reference files).

##### Expected Output (Optional)
```markdown
**Expected Output:**
JSON format with fields: name, value, date
```

Describes the format you expect the LLM to produce.

##### Verification (Optional)
```markdown
**Verification:**
- Must contain X
- Must have Y value > 0
- Should include Z
```

Rules that the output must satisfy. If verification fails, the step is retried.

##### Type (Optional)
```markdown
**Type:**
instruction
```

Options: `instruction`, `load_file`, `verification`, `transformation`, `custom`

Default is `instruction`.

### 6. Final Output Format (Optional)

Describes what the final output should look like:

```markdown
## Final Output Format
The final output should be a complete credit memo in professional business format,
including executive summary, analysis, and recommendations.
```

### 7. Success Criteria (Optional)

Defines when the skill is considered successful:

```markdown
## Success Criteria
The skill is successful when:
1. All financial data is accurately extracted
2. Risk assessment is thorough and logical
3. Final memo is complete and professional
4. All verification checks pass
```

## Advanced Features

### Variable Extraction

You can extract variables from step outputs to use in later steps:

```markdown
### Step 1: Calculate Revenue

**Instruction:**
Calculate total revenue and output as: Revenue: $X

**Variables to Extract:**
- revenue
```

The framework will attempt to extract the `revenue` variable and make it available in the luggage.

### Dependencies

Specify which steps must complete before this step:

```markdown
### Step 3: Generate Report

**Depends On:**
- 1
- 2
```

This step won't execute until steps 1 and 2 are complete.

### Verification Options

Control how verification failures are handled:

```markdown
**Verification:**
- Must contain revenue field
- Must contain expenses field

**Verification Settings:**
- Max Retries: 5
- Fail Action: halt  # Options: halt, skip, continue
```

**Fail Actions:**
- `halt` - Stop execution if verification fails
- `skip` - Skip this step and continue
- `continue` - Continue with the output despite failure (default)

## Best Practices

### 1. Clear Instructions

❌ Bad:
```markdown
**Instruction:**
Analyze the data.
```

✅ Good:
```markdown
**Instruction:**
Analyze the financial data and calculate the following ratios:
1. Current Ratio = Current Assets / Current Liabilities
2. Debt-to-Equity = Total Debt / Shareholders' Equity

Present results in a table format with ratio names and values.
```

### 2. Specific Verification

❌ Bad:
```markdown
**Verification:**
- Output should be good
```

✅ Good:
```markdown
**Verification:**
- Must contain all 5 calculated ratios
- Each ratio must have a numeric value
- Must include ratio names and formulas
```

### 3. Structured Output

Guide the LLM to produce structured output:

```markdown
**Expected Output:**
JSON format:
{
  "company_name": "string",
  "revenue": number,
  "expenses": number,
  "net_income": number
}
```

### 4. Progressive Complexity

Build complexity gradually across steps:

```markdown
### Step 1: Extract raw data
### Step 2: Calculate basic metrics
### Step 3: Perform advanced analysis
### Step 4: Generate final report
```

### 5. Use Context Effectively

Provide relevant context without overwhelming:

```markdown
## Context
This skill follows the Standard Credit Analysis Framework (SCAF).
Key principles:
- Risk assessment based on 3 categories: profitability, liquidity, leverage
- Ratios compared against industry benchmarks
- Final recommendation must align with risk rating
```

## Example: Simple Data Extraction Skill

```markdown
# Skill Name: Invoice Data Extractor

## Metadata
- Version: 1.0.0
- Author: SkillEngine Team
- Description: Extracts structured data from invoice documents
- Tags: extraction, invoice, data

## Context
This skill extracts key information from invoice documents and outputs
structured JSON data suitable for accounting systems.

## Steps

### Step 1: Extract Invoice Details

**Instruction:**
Extract the following information from the invoice:
- Invoice number
- Date
- Vendor name
- Total amount
- Line items (description, quantity, unit price, total)

Output as JSON.

**Reference Files:**
- input/invoice.pdf

**Expected Output:**
JSON with fields: invoice_number, date, vendor_name, total_amount, line_items

**Verification:**
- Must contain invoice_number field
- Must contain date field
- Must contain vendor_name field
- Must contain total_amount as a number
- Line items must be an array

### Step 2: Validate and Format

**Instruction:**
Validate the extracted data:
1. Ensure line items sum to total amount
2. Check date format is YYYY-MM-DD
3. Format currency values to 2 decimal places

Output the validated and formatted JSON.

**Expected Output:**
Valid JSON with all fields properly formatted

**Verification:**
- Date must be in YYYY-MM-DD format
- All currency values must have 2 decimal places
- Sum of line items must equal total_amount

## Final Output Format
Valid JSON object with all invoice data extracted and validated.

## Success Criteria
1. All required fields are extracted
2. Data validation passes
3. Output is valid JSON
```

## Tips and Tricks

1. **Test Incrementally**: Start with one step, test it, then add more
2. **Use Real Examples**: Include example outputs in your instructions
3. **Be Specific**: The more specific your instructions, the better the results
4. **Leverage Previous Steps**: Reference previous step outputs in later steps
5. **Verify Early**: Add verification to catch errors early in the workflow
6. **Keep Steps Focused**: Each step should do one thing well
7. **Document Edge Cases**: Note special cases in your instructions

## Troubleshooting

### Step Verification Keeps Failing

- Check if verification rules are too strict
- Ensure expected output format matches what you're verifying
- Increase max retries if needed
- Add more detail to the instruction

### LLM Not Following Instructions

- Make instructions more explicit and detailed
- Add examples of expected output
- Break complex steps into smaller steps
- Adjust temperature (lower = more focused)

### File Loading Errors

- Check file paths are correct (relative to project root)
- Ensure files exist and are readable
- Verify file formats are supported
- Use absolute paths if relative paths aren't working

## Need Help?

- Check existing skills in `skills/` for examples
- Review the [main README](../README.md) for framework documentation
- Open an issue on GitHub for bugs or feature requests

---

Happy skill building! 🚀
