"""
Unit tests for SkillMarkdownParser
"""

import pytest
from pathlib import Path
from skill_engine.parser.markdown_parser import SkillMarkdownParser
from skill_engine.models.skill import Skill, SkillStep


class TestSkillMarkdownParser:
    """Test cases for SkillMarkdownParser."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance."""
        return SkillMarkdownParser()

    @pytest.fixture
    def sample_markdown(self):
        """Sample markdown content for testing."""
        return """# Skill Name: Test Skill

## Metadata
- Version: 1.0.0
- Author: Test Author
- Description: A test skill
- Tags: test, demo

## Context
This is test context for the skill.

## Reference Files
- file1.txt
- file2.pdf

## Steps

### Step 1: First Step

**Instruction:**
Do the first thing.

**Reference Files:**
- step1_file.txt

**Expected Output:**
JSON format

**Verification:**
- Must contain field1
- Must contain field2

### Step 2: Second Step

**Instruction:**
Do the second thing.

## Final Output Format
The final output should be JSON.

## Success Criteria
All steps complete successfully.
"""

    def test_parse_markdown_basic(self, parser, sample_markdown):
        """Test basic markdown parsing."""
        skill = parser.parse_markdown(sample_markdown)

        assert isinstance(skill, Skill)
        assert skill.metadata.name == "Test Skill"
        assert skill.metadata.version == "1.0.0"
        assert skill.metadata.author == "Test Author"

    def test_parse_metadata(self, parser, sample_markdown):
        """Test metadata parsing."""
        skill = parser.parse_markdown(sample_markdown)

        assert skill.metadata.name == "Test Skill"
        assert skill.metadata.version == "1.0.0"
        assert skill.metadata.author == "Test Author"
        assert skill.metadata.description == "A test skill"
        assert "test" in skill.metadata.tags
        assert "demo" in skill.metadata.tags

    def test_parse_context(self, parser, sample_markdown):
        """Test context parsing."""
        skill = parser.parse_markdown(sample_markdown)
        assert skill.context == "This is test context for the skill."

    def test_parse_reference_files(self, parser, sample_markdown):
        """Test global reference files parsing."""
        skill = parser.parse_markdown(sample_markdown)

        assert len(skill.global_reference_files) == 2
        assert "file1.txt" in skill.global_reference_files
        assert "file2.pdf" in skill.global_reference_files

    def test_parse_steps(self, parser, sample_markdown):
        """Test steps parsing."""
        skill = parser.parse_markdown(sample_markdown)

        assert len(skill.steps) == 2

        # Check first step
        step1 = skill.steps[0]
        assert step1.step_number == 1
        assert step1.name == "First Step"
        assert "Do the first thing" in step1.instruction
        assert "step1_file.txt" in step1.reference_files

        # Check second step
        step2 = skill.steps[1]
        assert step2.step_number == 2
        assert step2.name == "Second Step"

    def test_parse_verification(self, parser, sample_markdown):
        """Test verification criteria parsing."""
        skill = parser.parse_markdown(sample_markdown)

        step1 = skill.steps[0]
        assert step1.verification is not None
        assert len(step1.verification.rules) == 2
        assert "field1" in step1.verification.required_elements
        assert "field2" in step1.verification.required_elements

    def test_parse_final_output(self, parser, sample_markdown):
        """Test final output format parsing."""
        skill = parser.parse_markdown(sample_markdown)
        assert "JSON" in skill.final_output_format

    def test_parse_success_criteria(self, parser, sample_markdown):
        """Test success criteria parsing."""
        skill = parser.parse_markdown(sample_markdown)
        assert "All steps complete" in skill.success_criteria

    def test_validate_dependencies(self, parser):
        """Test dependency validation."""
        markdown = """# Test Skill

## Steps

### Step 1: First
**Instruction:** Do first thing

### Step 2: Second
**Instruction:** Do second thing
**Depends On:** 1
"""
        skill = parser.parse_markdown(markdown)
        assert skill.validate_dependencies() is True

    def test_get_step(self, parser, sample_markdown):
        """Test getting a specific step."""
        skill = parser.parse_markdown(sample_markdown)

        step1 = skill.get_step(1)
        assert step1 is not None
        assert step1.name == "First Step"

        step_none = skill.get_step(999)
        assert step_none is None

    def test_get_total_steps(self, parser, sample_markdown):
        """Test getting total steps count."""
        skill = parser.parse_markdown(sample_markdown)
        assert skill.get_total_steps() == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
