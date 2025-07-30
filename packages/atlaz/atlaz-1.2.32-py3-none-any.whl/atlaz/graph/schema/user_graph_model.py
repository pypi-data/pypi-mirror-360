from typing import List, Optional
from pydantic import BaseModel, Field

class Node(BaseModel):
    id: str = Field(..., description="Unique identifier of the node.")
    label: str = Field(..., description="Human-readable label of the node.")
    color: str = Field(..., description="Color used to represent the node.")
    shape: str = Field(..., description="Shape used to represent the node, e.g., 'ellipse', 'box', etc.")
    info: Optional[str] = Field(None, description="Additional descriptive information about the node.")
    references: Optional[List[str]] = Field(None, description="List of reference strings (e.g. text-source snippets).")

class Edge(BaseModel):
    source: str = Field(..., description="ID of the source node.")
    target: str = Field(..., description="ID of the target node.")
    type: Optional[str] = Field(None, description="Type of relationship, e.g., 'subtype' or 'other'.")
    color: str = Field(..., description="Color used to represent the edge.")
    arrowhead: str = Field(..., description="Shape of the arrowhead, e.g., 'normal', 'diamond'.")
    label: Optional[str] = Field(None, description="Optional label for the edge relationship.")
    info: Optional[str] = Field(None, description="Additional motivation or description of the relationship.")
    references: Optional[List[str]] = Field(None, description="List of reference strings (e.g. text-source snippets).")

class Category(BaseModel):
    name: str = Field(..., description="Name of the category.")
    color: str = Field(..., description="Color used to represent the category.")

class Graph(BaseModel):
    nodes: List[Node] = Field(..., description="List of nodes in the graph.")
    edges: List[Edge] = Field(..., description="List of edges in the graph.")
    categories: List[Category] = Field(..., description="List of categories associated with the graph.")