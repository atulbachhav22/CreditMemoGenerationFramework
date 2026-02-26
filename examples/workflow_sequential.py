"""
Example: Sequential Skill Workflow

Demonstrates executing multiple skills sequentially where:
1. Financial Analysis skill extracts and analyzes financial data
2. Credit Memo Generation skill uses analysis output to create professional memo

Automatically detects available API keys (OpenAI or Anthropic) from .env
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

from skill_engine import SkillProcessor, WorkflowBuilder, get_available_llm_config, get_llm_display_name

load_dotenv()


def main():
    """Execute sequential workflow with skill chaining."""
    
    try:
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
            verbose=True
        )
        
        # Build workflow
        builder = WorkflowBuilder(verbose=True)
        
        # Step 1: Financial Analysis
        # This skill extracts financial data, calculates ratios, and performs risk assessment
        builder.add_skill(
            name="financial_analysis",
            skill_path="skills/financial_analysis.md",
            processor=processor,
            initial_variables={
                "analyst_name": "Jane Doe",
                "date": "2024-01-15"
            }
        )
        
        # Step 2: Credit Memo Generation
        # This skill depends on financial_analysis and uses its output as input
        builder.add_skill(
            name="credit_memo_generation",
            skill_path="skills/credit_memo_generation.md",
            processor=processor,
            dependencies=["financial_analysis"],
            initial_variables={
                "analyst_name": "Jane Doe",
                "date": "2024-01-15"
            }
        )
        
        # Build and execute sequential workflow
        print("\n" + "=" * 80)
        print("Sequential Workflow: Financial Analysis → Credit Memo Generation")
        print("=" * 80 + "\n")
        
        workflow = builder.build_sequential()
        results = workflow.execute()
        
        # Access results
        print("\n" + "=" * 80)
        print("WORKFLOW RESULTS")
        print("=" * 80)
        
        for skill_name, luggage in results.items():
            print(f"\n{'─' * 80}")
            print(f"Skill: {skill_name}")
            print(f"{'─' * 80}")
            print(f"  Completed at: {luggage.started_at}")
            print(f"  Steps executed: {len(luggage.step_outputs)}")
            print(f"  Variables extracted: {list(luggage.variables.keys())}")
            
            if luggage.step_outputs:
                print(f"\n  Step Outputs:")
                for step_name, output in luggage.step_outputs.items():
                    preview = output[:150] if len(output) > 150 else output
                    preview = preview.replace('\n', ' ')
                    print(f"    {step_name}: {preview}...")
            
            # Display verification results
            if luggage.verification_results:
                print(f"\n  Verification Results:")
                for step, passed in luggage.verification_results.items():
                    status = "✓ PASSED" if passed else "✗ FAILED"
                    print(f"    {step}: {status}")
        
        # Export results
        output_dir = Path("output/workflow_sequential")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'─' * 80}")
        print("Exporting Results")
        print(f"{'─' * 80}\n")
        
        for skill_name, luggage in results.items():
            json_path = str(output_dir / f"{skill_name}_result.json")
            txt_path = str(output_dir / f"{skill_name}_result.txt")
            
            processor.export_results(
                luggage,
                output_path=json_path,
                format="json"
            )
            print(f"✓ Exported JSON: {json_path}")
            
            processor.export_results(
                luggage,
                output_path=txt_path,
                format="text"
            )
            print(f"✓ Exported TXT: {txt_path}")
        
        # Display final memo
        print(f"\n{'─' * 80}")
        print("FINAL CREDIT MEMO (from credit_memo_generation)")
        print(f"{'─' * 80}\n")
        
        if "credit_memo_generation" in results:
            final_memo_luggage = results["credit_memo_generation"]
            if final_memo_luggage.step_outputs:
                # Get the last step output (final memo with analyst info)
                last_output = list(final_memo_luggage.step_outputs.values())[-1]
                print(last_output)
        
        print(f"\n{'─' * 80}")
        print("✓ Sequential workflow completed successfully!")
        print(f"{'─' * 80}\n")
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error executing workflow: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()