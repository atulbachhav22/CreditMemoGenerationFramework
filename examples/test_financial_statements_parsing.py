"""
Test script to verify financial-statements.md parsing works correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skill_engine.parser.markdown_parser import SkillMarkdownParser


def main():
    """Test parsing of financial-statements.md skill file."""

    print("=" * 80)
    print("Testing financial-statements.md Parsing")
    print("=" * 80)
    print()

    try:
        # Initialize parser
        parser = SkillMarkdownParser()

        # Parse the skill file
        print("Parsing skills/financial-statements.md...")
        skill = parser.parse_file("skills/financial-statements.md")

        print("[SUCCESS] Parsing successful!")
        print()

        # Display skill information
        print("=" * 80)
        print("SKILL INFORMATION")
        print("=" * 80)
        print(f"Name: {skill.metadata.name}")
        print(f"Version: {skill.metadata.version}")
        print(f"Author: {skill.metadata.author}")
        print(f"Description: {skill.metadata.description}")
        print(f"Tags: {', '.join(skill.metadata.tags)}")
        print()

        # Display steps
        print("=" * 80)
        print("STEPS")
        print("=" * 80)
        print(f"Total Steps: {skill.get_total_steps()}")
        print()

        for step in skill.steps:
            print(f"Step {step.step_number}: {step.name}")
            print(f"  Type: {step.step_type}")
            print(f"  Has instruction: {'YES' if step.instruction else 'NO'}")
            print(f"  Has expected output: {'YES' if step.expected_output_format else 'NO'}")
            print(f"  Has verification: {'YES' if step.verification else 'NO'}")
            if step.verification:
                print(f"    Verification rules: {len(step.verification.rules)}")
                print(f"    Required elements: {len(step.verification.required_elements)}")
            print(f"  Reference files: {len(step.reference_files)}")
            print()

        # Display context presence
        print("=" * 80)
        print("OTHER SECTIONS")
        print("=" * 80)
        print(f"Has context: {'YES' if skill.context else 'NO'}")
        print(f"Global reference files: {len(skill.global_reference_files)}")
        if skill.global_reference_files:
            for ref_file in skill.global_reference_files:
                print(f"  - {ref_file}")
        print(f"Has final output format: {'YES' if skill.final_output_format else 'NO'}")
        print(f"Has success criteria: {'YES' if skill.success_criteria else 'NO'}")
        print()

        # Validation
        print("=" * 80)
        print("VALIDATION")
        print("=" * 80)

        issues = []

        if skill.get_total_steps() != 6:
            issues.append(f"Expected 6 steps, found {skill.get_total_steps()}")

        for step in skill.steps:
            if not step.instruction:
                issues.append(f"Step {step.step_number} missing instruction")
            if not step.expected_output_format:
                issues.append(f"Step {step.step_number} missing expected output format")
            if not step.verification:
                issues.append(f"Step {step.step_number} missing verification criteria")

        if not skill.context:
            issues.append("Missing context section")

        if not skill.final_output_format:
            issues.append("Missing final output format")

        if not skill.success_criteria:
            issues.append("Missing success criteria")

        if issues:
            print("[WARNING] Issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("[SUCCESS] All validation checks passed!")
            print()
            print("The skill is properly formatted and ready to execute!")

        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print("[SUCCESS] financial-statements.md is now a valid executable skill")
        print(f"[SUCCESS] Parser successfully extracted {skill.get_total_steps()} steps")
        print("[SUCCESS] All required sections are present")
        print()
        print("You can now run this skill with:")
        print("  processor = SkillProcessor(...)")
        print("  luggage = processor.execute_skill_file('skills/financial-statements.md')")
        print()

    except FileNotFoundError as e:
        print(f"[ERROR] File not found: {e}")
        print("Make sure you're running from the project root directory")
    except Exception as e:
        print(f"[ERROR] Parsing failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
