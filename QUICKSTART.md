# SkillEngine Quick Start Guide

Get up and running with SkillEngine in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up Your API Key

Create a `.env` file in the project root:

```bash
# For OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# OR for Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Step 3: Run the Example

```bash
python examples/run_credit_memo.py
```

This will:
1. Load the Credit Memo skill from `skills/credit_memo.md`
2. Process the sample financial statement
3. Execute all 4 steps with verification
4. Generate a complete credit memo
5. Export results to `output/` directory

## Step 4: View the Results

Check the `output/` directory for:
- `credit_memo_result.json` - Full execution data
- `credit_memo_result.txt` - Readable output

## What Just Happened?

The framework:

1. **Parsed** the [credit_memo.md](skills/credit_memo.md) skill file
2. **Loaded** the [financial_statement.txt](examples/sample_data/financial_statement.txt) reference file
3. **Executed** 4 sequential steps:
   - Extracted financial data
   - Calculated financial ratios
   - Performed risk assessment
   - Generated the credit memo
4. **Verified** each step's output against defined criteria
5. **Stored** all intermediate results in the SkillLuggage
6. **Returned** the final credit memo

## Understanding the Code

### Minimal Example

```python
from skill_engine import SkillProcessor

# Create processor
processor = SkillProcessor(
    llm_provider="openai",
    model_name="gpt-4",
    api_key="your-key"
)

# Execute skill
luggage = processor.execute_skill_file("skills/credit_memo.md")

# Get result
final_output = processor.get_final_output(luggage)
print(final_output)
```

### With Options

```python
from skill_engine import SkillProcessor
import os

processor = SkillProcessor(
    llm_provider="openai",
    model_name="gpt-4",
    temperature=0.0,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_path="./data",  # Base path for file loading
    verbose=True         # Show progress
)

luggage = processor.execute_skill_file(
    "skills/credit_memo.md",
    initial_variables={
        "analyst_name": "Jane Doe",
        "date": "2024-01-15"
    }
)

# Access specific outputs
step_1_output = luggage.get_step_output("Extract Financial Data")
revenue = luggage.get_variable("revenue")

# Export results
processor.export_results(luggage, "output/result.json", format="json")
```

## Next Steps

### 1. Explore the Credit Memo Skill

Open [skills/credit_memo.md](skills/credit_memo.md) to see how a skill is structured.

### 2. Create Your Own Skill

Read the [Skills Guide](skills/README.md) to learn how to create custom skills.

### 3. Try Different Use Cases

SkillEngine can handle:
- Data extraction from documents
- Multi-step analysis workflows
- Report generation
- Data transformation pipelines
- Quality assurance checks

### 4. Customize the Framework

Extend the framework:
- Add new file loaders
- Create custom step types
- Integrate different LLM providers
- Build domain-specific verification logic

## Common Tasks

### Change the LLM Provider

```python
# Use Anthropic Claude
processor = SkillProcessor(
    llm_provider="anthropic",
    model_name="claude-3-opus-20240229",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

### Access Intermediate Results

```python
luggage = processor.execute_skill_file("skills/credit_memo.md")

# Get all step outputs
for step_name, output in luggage.step_outputs.items():
    print(f"\n{step_name}:")
    print(output[:200])  # First 200 chars

# Get verification results
for step_name, passed in luggage.verification_results.items():
    print(f"{step_name}: {'✓' if passed else '✗'}")
```

### Debug a Skill

```python
# Enable verbose mode
processor = SkillProcessor(
    llm_provider="openai",
    model_name="gpt-4",
    verbose=True  # Shows detailed progress
)

# Check the luggage state
luggage = processor.execute_skill_file("skills/credit_memo.md")
print(luggage.get_context_summary())
```

## Troubleshooting

### API Key Issues

```
Error: Please set OPENAI_API_KEY...
```

**Solution:** Create a `.env` file with your API key or set it as an environment variable.

### File Not Found

```
FileNotFoundError: Skill file not found...
```

**Solution:** Run scripts from the project root directory or use absolute paths.

### Verification Failures

```
Verification failed (attempt 1/3)
```

**Solution:** This is normal - the framework will retry. If it keeps failing, check your verification criteria in the skill file.

## Resources

- **Full Documentation:** [README.md](README.md)
- **Skill Creation Guide:** [skills/README.md](skills/README.md)
- **Example Skill:** [skills/credit_memo.md](skills/credit_memo.md)
- **Sample Data:** [examples/sample_data/](examples/sample_data/)

## Need Help?

- Check the [README](README.md) for detailed documentation
- Look at [test files](tests/) for usage examples
- Open an issue on GitHub for support

---

**You're ready to go! Start creating your own skills and automate complex LLM workflows.** 🚀
