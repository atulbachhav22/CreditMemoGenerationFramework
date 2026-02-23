"""
Unit tests for SkillProcessor
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from skill_engine.processor.skill_processor import SkillProcessor
from skill_engine.models.skill import Skill, SkillStep, SkillMetadata
from skill_engine.models.luggage import SkillLuggage


class TestSkillProcessor:
    """Test cases for SkillProcessor."""

    @pytest.fixture
    def mock_llm_orchestrator(self):
        """Create a mock LLM orchestrator."""
        with patch('skill_engine.processor.skill_processor.LLMOrchestrator') as mock:
            orchestrator = Mock()
            orchestrator.execute_step.return_value = "Mock output"
            orchestrator.verify_output.return_value = (True, "Verification passed")
            orchestrator.model_name = "gpt-4"
            mock.return_value = orchestrator
            yield orchestrator

    @pytest.fixture
    def processor(self, mock_llm_orchestrator):
        """Create a processor instance with mocked LLM."""
        return SkillProcessor(
            llm_provider="openai",
            model_name="gpt-4",
            verbose=False
        )

    @pytest.fixture
    def simple_skill(self):
        """Create a simple test skill."""
        return Skill(
            metadata=SkillMetadata(
                name="Test Skill",
                version="1.0.0"
            ),
            context="Test context",
            steps=[
                SkillStep(
                    step_number=1,
                    name="Test Step",
                    instruction="Do something"
                )
            ]
        )

    def test_processor_initialization(self, processor):
        """Test processor initialization."""
        assert processor is not None
        assert processor.parser is not None
        assert processor.orchestrator is not None
        assert processor.file_loader is not None

    def test_execute_skill_basic(self, processor, simple_skill, mock_llm_orchestrator):
        """Test basic skill execution."""
        luggage = processor.execute_skill(simple_skill)

        assert isinstance(luggage, SkillLuggage)
        assert luggage.skill_name == "Test Skill"
        assert len(luggage.step_outputs) == 1
        assert "Test Step" in luggage.step_outputs

    def test_execute_skill_with_variables(self, processor, simple_skill, mock_llm_orchestrator):
        """Test skill execution with initial variables."""
        initial_vars = {"var1": "value1", "var2": 123}

        luggage = processor.execute_skill(simple_skill, initial_variables=initial_vars)

        assert luggage.get_variable("var1") == "value1"
        assert luggage.get_variable("var2") == 123

    def test_get_final_output(self, processor, simple_skill, mock_llm_orchestrator):
        """Test getting final output."""
        luggage = processor.execute_skill(simple_skill)
        final_output = processor.get_final_output(luggage)

        assert final_output == "Mock output"

    def test_export_results_json(self, processor, tmp_path):
        """Test exporting results as JSON."""
        luggage = SkillLuggage(skill_name="Test")
        luggage.add_step_output("Step 1", "Output 1")

        output_file = tmp_path / "result.json"
        processor.export_results(luggage, str(output_file), format="json")

        assert output_file.exists()

    def test_export_results_text(self, processor, tmp_path):
        """Test exporting results as text."""
        luggage = SkillLuggage(skill_name="Test")
        luggage.add_step_output("Step 1", "Output 1")

        output_file = tmp_path / "result.txt"
        processor.export_results(luggage, str(output_file), format="text")

        assert output_file.exists()


class TestSkillLuggage:
    """Test cases for SkillLuggage."""

    def test_luggage_initialization(self):
        """Test luggage initialization."""
        luggage = SkillLuggage(skill_name="Test Skill")

        assert luggage.skill_name == "Test Skill"
        assert len(luggage.variables) == 0
        assert len(luggage.step_outputs) == 0
        assert luggage.started_at is not None

    def test_set_and_get_variable(self):
        """Test setting and getting variables."""
        luggage = SkillLuggage()

        luggage.set_variable("key1", "value1")
        assert luggage.get_variable("key1") == "value1"

        luggage.set_variable("key2", 123)
        assert luggage.get_variable("key2") == 123

    def test_add_and_get_step_output(self):
        """Test adding and getting step outputs."""
        luggage = SkillLuggage()

        luggage.add_step_output("Step 1", "Output from step 1")
        assert luggage.get_step_output("Step 1") == "Output from step 1"

    def test_load_and_get_file_content(self):
        """Test loading and getting file content."""
        luggage = SkillLuggage()

        luggage.load_file_content("file1.txt", "File content here")
        assert luggage.get_file_content("file1.txt") == "File content here"

    def test_record_verification(self):
        """Test recording verification results."""
        luggage = SkillLuggage()

        luggage.record_verification("Step 1", True)
        luggage.record_verification("Step 2", False)

        assert luggage.verification_results["Step 1"] is True
        assert luggage.verification_results["Step 2"] is False

    def test_context_summary(self):
        """Test generating context summary."""
        luggage = SkillLuggage()

        luggage.set_variable("revenue", 10000)
        luggage.add_step_output("Step 1", "Some output")

        summary = luggage.get_context_summary()

        assert "revenue" in summary
        assert "10000" in summary
        assert "Step 1" in summary

    def test_to_dict(self):
        """Test converting luggage to dictionary."""
        luggage = SkillLuggage(skill_name="Test")
        luggage.set_variable("var1", "value1")
        luggage.add_step_output("Step 1", "Output 1")

        result = luggage.to_dict()

        assert isinstance(result, dict)
        assert result["skill_name"] == "Test"
        assert "var1" in result["variables"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
