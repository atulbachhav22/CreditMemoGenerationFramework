"""
Simple Example: Quick Start with SkillEngine

This demonstrates the simplest way to use SkillEngine.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

from skill_engine import SkillProcessor

# Load environment variables
load_dotenv()


def main():
    """Simple example of using SkillEngine."""

    # Create processor - Choose one:

    # Option 1: OpenAI
    # processor = SkillProcessor(
    #     llm_provider="openai",
    #     model_name="gpt-4",
    #     api_key=os.getenv("OPENAI_API_KEY")
    # )

    # Option 2: Anthropic Claude (recommended)
    processor = SkillProcessor(
        llm_provider="anthropic",
        model_name="claude-3-5-sonnet-20240620",  # Stable and widely available
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    # Execute skill
    luggage = processor.execute_skill_file("skills/credit_memo.md")

    # Get final output
    final_output = processor.get_final_output(luggage)
    print(final_output)


if __name__ == "__main__":
    main()
