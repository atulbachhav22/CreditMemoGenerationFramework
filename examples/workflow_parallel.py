"""
Example: Parallel Skill Workflow

Demonstrates executing multiple independent skills in parallel where
skills run concurrently without dependencies.

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
    """Execute parallel workflow."""
    
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
        
        # Add independent skills (no dependencies) - will run in parallel
        builder.add_skill(
            name="financial_analysis_1",
            skill_path="skills/financial_analysis.md",
            processor=processor,
            initial_variables={
                "analyst_name": "Analyst A",
                "date": "2024-01-15"
            }
        )
        
        builder.add_skill(
            name="financial_analysis_2",
            skill_path="skills/financial_analysis.md",
            processor=processor,
            initial_variables={
                "analyst_name": "Analyst B",
                "date": "2024-01-15"
            }
        )
        
        # builder.add_skill(
        #     name="financial_analysis_3",
        #     skill_path="skills/financial_analysis.md",
        #     processor=processor,
        #     initial_variables={
        #         "analyst_name": "Analyst C",
        #         "date": "2024-01-15"
        #     }
        # )
        
        # Build and execute parallel workflow
        print("\n" + "=" * 80)
        print("Parallel Workflow: 3 Financial Analysis Skills (Concurrent)")
        print("=" * 80 + "\n")
        
        workflow = builder.build_parallel(max_workers=3)
        results = workflow.execute()
        
        # Access results
        print("\n" + "=" * 80)
        print("PARALLEL WORKFLOW RESULTS")
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
                    preview = output[:100] if len(output) > 100 else output
                    preview = preview.replace('\n', ' ')
                    print(f"    {step_name}: {preview}...")
            
            # Display verification results
            if luggage.verification_results:
                print(f"\n  Verification Results:")
                for step, passed in luggage.verification_results.items():
                    status = "✓ PASSED" if passed else "✗ FAILED"
                    print(f"    {step}: {status}")
        
        # Export results
        output_dir = Path("output/workflow_parallel")
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
        
        print(f"\n{'─' * 80}")
        print("✓ Parallel workflow completed successfully!")
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