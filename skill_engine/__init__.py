"""
SkillEngine - A robust Python framework for executing LLM-orchestrated Skills.

This framework allows you to define complex, multi-step LLM workflows in Markdown files
and execute them with state management, verification loops, and extensibility.
"""

from skill_engine.models.skill import Skill, SkillStep, SkillMetadata
from skill_engine.models.luggage import SkillLuggage
from skill_engine.models.workflow import WorkflowDefinition, WorkflowNode, WorkflowEdge
from skill_engine.processor.skill_processor import SkillProcessor
from skill_engine.parser.markdown_parser import SkillMarkdownParser
from skill_engine.pipeline.pipeline_orchestrator import PipelineOrchestrator, PipelineResult

__version__ = "0.1.0"
__all__ = [
    "Skill",
    "SkillStep",
    "SkillMetadata",
    "SkillLuggage",
    "WorkflowDefinition",
    "WorkflowNode",
    "WorkflowEdge",
    "SkillProcessor",
    "SkillMarkdownParser",
    "PipelineOrchestrator",
    "PipelineResult",
]
