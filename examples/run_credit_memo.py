"""
Example: Running the Credit Memo Generator Skill

This script demonstrates how to use the SkillEngine framework to execute
the Credit Memo Generator skill.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to import skill_engine
sys.path.insert(0, str(Path(__file__).parent.parent))

from skill_engine import SkillProcessor, get_available_llm_config, get_llm_display_name

# Load environment variables from .env file
load_dotenv()


def main():
    """Execute the Credit Memo Generator skill."""

    # Configuration
    skill_file = "skills/credit_memo.md"

    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")  # or ANTHROPIC_API_KEY

    # Detect available LLM
    provider, model, api_key = get_available_llm_config()
    display_name = get_llm_display_name(provider, model)
    
    print("\n" + "=" * 80)
    print(f"Using: {display_name}")
    print("=" * 80)
    
    # Initialize processor with detected LLM
    processor = SkillProcessor(
        llm_provider=provider,
        model_name=model,
        api_key=api_key,
        temperature=0.0,
        verbose=True
    )

    print("=" * 80)
    print("Credit Memo Generator - SkillEngine Demo")
    print("=" * 80)
    print()

    # Execute the skill
    try:
        luggage = processor.execute_skill_file(
            skill_file_path=skill_file,
            initial_variables={
                "analyst_name": "John Doe",
                "date": "2024-01-15"
            }
        )

        # Get the final credit memo
        final_output = processor.get_final_output(luggage)

        print("\n" + "=" * 80)
        print("FINAL CREDIT MEMO")
        print("=" * 80)
        print()
        print(final_output)
        print()

        # Export results
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        # Export as JSON
        processor.export_results(
            luggage,
            output_path="output/credit_memo_result.json",
            format="json"
        )
        print("✓ Results exported to: output/credit_memo_result.json")

        # Export as text
        processor.export_results(
            luggage,
            output_path="output/credit_memo_result.txt",
            format="text"
        )
        print("✓ Results exported to: output/credit_memo_result.txt")

        # Display execution summary
        print("\n" + "=" * 80)
        print("EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Skill: {luggage.skill_name}")
        print(f"Steps Completed: {len(luggage.step_outputs)}")
        print(f"Started: {luggage.started_at}")
        print(f"Model Used: {luggage.execution_metadata.get('model_used', 'N/A')}")
        print()

        # Display verification results
        if luggage.verification_results:
            print("Verification Results:")
            for step, passed in luggage.verification_results.items():
                status = "✓ PASSED" if passed else "✗ FAILED"
                print(f"  {step}: {status}")
            print()

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure you're running this script from the project root directory")
    except Exception as e:
        print(f"Error executing skill: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
