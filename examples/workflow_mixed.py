"""
Example: Mixed Sequential and Parallel Workflow

Demonstrates a workflow where:
- Skills A, B, C run in parallel
- Then skill D depends on completion of A, B, C
- Skills E and F run in parallel (depending on D)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

from skill_engine import SkillProcessor
from skill_engine.processor import WorkflowBuilder

load_dotenv()


def main():
    """Execute mixed workflow."""
    
    processor = SkillProcessor(
        llm_provider="anthropic",
        model_name="claude-3-5-sonnet-20241022",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        verbose=True
    )
    
    builder = WorkflowBuilder(verbose=True)
    
    # Parallel phase 1: A, B, C
    builder.add_skill(
        name="data_extraction_A",
        skill_path="skills/credit_memo.md",
        processor=processor,
        initial_variables={"source": "Financial Statement A"}
    )
    
    builder.add_skill(
        name="data_extraction_B",
        skill_path="skills/credit_memo.md",
        processor=processor,
        initial_variables={"source": "Financial Statement B"}
    )
    
    builder.add_skill(
        name="data_extraction_C",
        skill_path="skills/credit_memo.md",
        processor=processor,
        initial_variables={"source": "Financial Statement C"}
    )
    
    # Sequential phase: D depends on A, B, C
    builder.add_skill(
        name="aggregation",
        skill_path="skills/credit_memo.md",
        processor=processor,
        dependencies=["data_extraction_A", "data_extraction_B", "data_extraction_C"],
        initial_variables={"operation": "aggregate"}
    )
    
    # Parallel phase 2: E, F depend on D
    builder.add_skill(
        name="final_analysis_E",
        skill_path="skills/credit_memo.md",
        processor=processor,
        dependencies=["aggregation"],
        initial_variables={"analysis_type": "risk"}
    )
    
    builder.add_skill(
        name="final_analysis_F",
        skill_path="skills/credit_memo.md",
        processor=processor,
        dependencies=["aggregation"],
        initial_variables={"analysis_type": "trend"}
    )
    
    # Build and execute with parallel execution respecting dependencies
    workflow = builder.build_parallel(max_workers=4)
    results = workflow.execute()
    
    print("\n" + "=" * 80)
    print("MIXED WORKFLOW RESULTS")
    print("=" * 80)
    
    for skill_name, luggage in results.items():
        print(f"\n{skill_name}:")
        print(f"  Steps: {len(luggage.step_outputs)}")
        print(f"  Verification passed: {sum(luggage.verification_results.values())}/{len(luggage.verification_results)}")


if __name__ == "__main__":
    main()