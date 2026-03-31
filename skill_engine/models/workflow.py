"""
WorkflowDefinition - Pydantic models for the workflow JSON format.

Represents a DAG of skill nodes connected by sequential or parallel edges,
as produced by the visual workflow editor.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class WorkflowNode(BaseModel):
    """A single skill node in the workflow graph."""

    id: str = Field(..., description="Unique node identifier")
    skill_name: str = Field(..., description="Name of the skill file (without .md extension)")
    label: str = Field(..., description="Human-readable display label")
    position: dict = Field(default_factory=dict, description="Visual position (x, y) — ignored at runtime")


class WorkflowEdge(BaseModel):
    """A directed edge between two nodes in the workflow graph."""

    id: str = Field(..., description="Unique edge identifier")
    source: str = Field(..., description="ID of the source node")
    target: str = Field(..., description="ID of the target node")
    edge_type: str = Field(
        default="sequential",
        description=(
            "Edge type: 'sequential' (default) or 'parallel'. "
            "'parallel' edges from the same source node indicate that all "
            "their targets can execute concurrently once the source completes."
        )
    )


class WorkflowDefinition(BaseModel):
    """
    Complete workflow definition parsed from a workflow JSON file.

    A workflow is a Directed Acyclic Graph (DAG) where:
    - Each node maps to a skill .md file
    - Each edge defines a dependency (source must complete before target starts)
    - Edges marked 'parallel' allow concurrent execution of sibling targets
    """

    id: str = Field(..., description="Unique workflow identifier")
    name: str = Field(..., description="Workflow name")
    description: str = Field(default="", description="Optional description")
    nodes: List[WorkflowNode] = Field(..., description="List of skill nodes")
    edges: List[WorkflowEdge] = Field(default_factory=list, description="List of directed edges")
    created_at: Optional[str] = Field(default=None)
    updated_at: Optional[str] = Field(default=None)

    def get_node(self, node_id: str) -> Optional[WorkflowNode]:
        """Look up a node by its ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def predecessors(self, node_id: str) -> List[str]:
        """Return IDs of all nodes that must complete before node_id."""
        return [e.source for e in self.edges if e.target == node_id]

    def successors(self, node_id: str) -> List[str]:
        """Return IDs of all nodes that depend on node_id."""
        return [e.target for e in self.edges if e.source == node_id]

    def start_nodes(self) -> List[str]:
        """Return IDs of nodes with no incoming edges (pipeline entry points)."""
        targets = {e.target for e in self.edges}
        return [n.id for n in self.nodes if n.id not in targets]
