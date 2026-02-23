# SkillEngine Framework

> A robust Python framework for executing LLM-orchestrated Skills defined in Markdown files

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

**SkillEngine** is a powerful, extensible framework that allows you to define complex, multi-step LLM workflows as simple Markdown documents. The framework handles:

- 📝 Parsing structured instructions from Markdown files
- 🔄 Sequential step execution with state management
- 📁 Dynamic file loading and context injection
- ✅ Automated verification loops
- 🎯 Skill-agnostic architecture (works with any task)
- 🤖 Multiple LLM providers (OpenAI, Anthropic)

## Key Features

### 🎯 Skill-Agnostic Design
Write any workflow once in Markdown, execute it anywhere. The framework doesn't care if you're generating credit memos, extracting data, or summarizing reports.

### 🧳 "Skill Luggage" State Management
A sophisticated state container that carries data between steps:
- Variables and intermediate results
- Previous step outputs
- Loaded file contents
- Verification results

### ✅ Built-in Verification Loops
Define verification criteria directly in your Markdown. The framework automatically:
- Checks output against criteria
- Retries failed steps with feedback
- Enforces quality standards

### 🔌 Extensible Architecture
- Support for multiple LLM providers (OpenAI, Anthropic)
- Custom step types
- Pluggable file loaders
- Easy to extend with new capabilities

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd CreditMemoGenerationFramework

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Set Up Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
# OPENAI_API_KEY=your_key_here
```

### Run Your First Skill

```python
from skill_engine import SkillProcessor

# Initialize processor
processor = SkillProcessor(
    llm_provider="openai",
    model_name="gpt-4",
    api_key="your-api-key"
)

# Execute a skill
luggage = processor.execute_skill_file("skills/credit_memo.md")

# Get final output
final_output = processor.get_final_output(luggage)
print(final_output)
```

### Run the Credit Memo Example

```bash
python examples/run_credit_memo.py
```

## Project Structure

```
CreditMemoGenerationFramework/
├── skill_engine/              # Core framework
│   ├── parser/                # Markdown parsing
│   ├── models/                # Data models (Pydantic)
│   ├── processor/             # Core execution engine
│   ├── llm/                   # LLM orchestration
│   └── utils/                 # Utilities (file loading, etc.)
├── skills/                    # Skill definitions (.md files)
│   └── credit_memo.md         # Example: Credit Memo Generator
├── examples/                  # Example scripts
│   ├── run_credit_memo.py     # Full example
│   ├── simple_example.py      # Minimal example
│   └── sample_data/           # Sample input files
├── tests/                     # Unit tests
├── requirements.txt           # Dependencies
├── setup.py                   # Package setup
└── README.md                  # This file
```

## Creating a Skill

Skills are defined in Markdown files with a specific structure:

```markdown
# Skill Name: Your Skill Name

## Metadata
- Version: 1.0.0
- Author: Your Name
- Description: What this skill does
- Tags: tag1, tag2

## Context
Background information that applies to the entire skill...

## Reference Files
- path/to/file1.txt
- path/to/file2.pdf

## Steps

### Step 1: First Step Name

**Instruction:**
What the LLM should do in this step...

**Reference Files:**
- specific_file_for_this_step.txt

**Expected Output:**
Description of expected format...

**Verification:**
- Must contain X
- Must have Y
- Should include Z

### Step 2: Second Step Name
...

## Final Output Format
Description of what the final output should look like...

## Success Criteria
What defines success for this skill...
```

See [skills/README.md](skills/README.md) for detailed documentation on creating skills.

## Architecture

### Core Components

1. **SkillMarkdownParser** - Parses .md files into structured `Skill` objects
2. **SkillProcessor** - Orchestrates execution of skills
3. **LLMOrchestrator** - Manages LLM interactions via LangChain
4. **SkillLuggage** - State container that carries data between steps
5. **FileLoader** - Loads various file types (PDF, DOCX, TXT, etc.)

### Execution Flow

```
1. Parse Markdown → Skill object
2. Initialize SkillLuggage (state)
3. For each step:
   a. Load reference files
   b. Build LLM prompt with context
   c. Execute LLM call
   d. Verify output (if criteria specified)
   e. Store output in luggage
   f. Extract variables (if specified)
4. Return final luggage with all outputs
```

## Configuration

### LLM Providers

#### OpenAI

```python
processor = SkillProcessor(
    llm_provider="openai",
    model_name="gpt-4",  # or gpt-4-turbo-preview, gpt-3.5-turbo
    temperature=0.0,
    api_key=os.getenv("OPENAI_API_KEY")
)
```

#### Anthropic (Claude)

```python
processor = SkillProcessor(
    llm_provider="anthropic",
    model_name="claude-3-opus-20240229",  # or claude-3-sonnet-20240229
    temperature=0.0,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

### Advanced Options

```python
processor = SkillProcessor(
    llm_provider="openai",
    model_name="gpt-4",
    temperature=0.0,
    base_path="./data",  # Base path for resolving relative file paths
    verbose=True,        # Enable rich console output
    max_tokens=4000,     # Additional LLM parameters
    top_p=0.9
)
```

## Examples

### Basic Usage

```python
from skill_engine import SkillProcessor

processor = SkillProcessor(
    llm_provider="openai",
    model_name="gpt-4"
)

luggage = processor.execute_skill_file("skills/credit_memo.md")
final_output = processor.get_final_output(luggage)
```

### With Initial Variables

```python
luggage = processor.execute_skill_file(
    "skills/credit_memo.md",
    initial_variables={
        "analyst_name": "Jane Doe",
        "date": "2024-01-15",
        "custom_param": "value"
    }
)
```

### Exporting Results

```python
# Export as JSON
processor.export_results(
    luggage,
    output_path="output/result.json",
    format="json"
)

# Export as text
processor.export_results(
    luggage,
    output_path="output/result.txt",
    format="text"
)
```

### Accessing Step Outputs

```python
# Get specific step output
step_1_output = luggage.get_step_output("Extract Financial Data")

# Get all outputs
all_outputs = luggage.step_outputs

# Get variables
revenue = luggage.get_variable("revenue")
```

## Use Cases

SkillEngine is perfect for:

- 📊 **Financial Analysis** - Credit memos, risk assessment, financial reporting
- 📄 **Document Processing** - Data extraction, summarization, classification
- 🔍 **Research Tasks** - Multi-step analysis, literature review, synthesis
- 📝 **Report Generation** - Automated report creation with multiple sections
- 🧪 **Data Transformation** - Multi-stage data processing pipelines
- ✅ **Quality Assurance** - Automated verification and validation workflows

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=skill_engine

# Run specific test file
pytest tests/test_parser.py
```

## Development

### Installing in Development Mode

```bash
pip install -e ".[dev]"
```

### Code Style

```bash
# Format code
black skill_engine/

# Sort imports
isort skill_engine/

# Type checking
mypy skill_engine/
```

## Roadmap

- [ ] Support for parallel step execution
- [ ] Conditional branching in skills
- [ ] More sophisticated variable extraction
- [ ] Support for more LLM providers (Cohere, etc.)
- [ ] Web UI for skill creation
- [ ] Skill marketplace/repository
- [ ] Streaming output support
- [ ] Advanced caching mechanisms

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain)
- Markdown parsing by [Mistune](https://github.com/lepture/mistune)
- Data validation with [Pydantic](https://github.com/pydantic/pydantic)
- Beautiful console output via [Rich](https://github.com/Textualize/rich)

## Support

For questions, issues, or feature requests, please open an issue on GitHub.

---

**Built with ❤️ for the LLM community**
