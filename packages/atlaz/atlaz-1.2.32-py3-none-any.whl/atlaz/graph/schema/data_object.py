from typing import List, Optional
from pydantic import BaseModel, Field

class Entity(BaseModel):
    """
    Basic entity in the start_object, with optional Definition or TaxonomyID.
    """
    ID: int = Field(..., description="Unique identifier of the entity.")
    Name: str = Field(..., description="Human-readable name of the entity.")
    Definition: Optional[str] = Field(None, description="Definition or description of the entity.")

class RelationshipEntity(BaseModel):
    """
    A 'RelationshipEntity' such as "Is A Type Of", "Has A Relationship To", etc.
    """
    ID: int = Field(..., description="Unique identifier of the relationship entity.")
    Name: str = Field(..., description="Human-readable name of the relationship entity.")
    Definition: Optional[str] = Field(None, description="Definition or description of the relationship entity.")
    SourceNodeTypeID: int = Field(..., description="ID of the abstract type the source entity can have.")
    TargetNodeTypeID: int = Field(..., description="ID of the abstract type the target entity can have.")
    Transitive: bool = Field(..., description="True if the relationship is transitive (A->B and B->C imply A->C).")
    Bidirectional: bool = Field(..., description="True if the relationship is bidirectional (A->B implies B->A).")

class Relationship(BaseModel):
    """
    A single relationship instance linking two nodes (SourceNodeID, TargetNodeID)
    via a 'RelationshipEntity' (EntityID).
    """
    ID: int = Field(..., description="Unique identifier for this specific relationship instance.")
    SourceNodeID: int = Field(..., description="ID of the source node in the relationship.")
    TargetNodeID: int = Field(..., description="ID of the target node in the relationship.")
    EntityID: int = Field(..., description="Which RelationshipEntity is used (e.g., 'Is A Type Of').")
    Motivation: Optional[str] = Field(None, description="Reason or motivation for why this relationship holds.")


class GraphObject(BaseModel):
    """
    The Pydantic model representing the entire `start_object` dictionary that
    `transform_graph_to_user` expects.
    """
    Entities: List[Entity] = Field(
        ..., description="List of domain Entities in the graph."
    )
    RelationshipEntities: List[RelationshipEntity] = Field(
        ..., description="List of special RelationshipEntities (like 'Is A Type Of')."
    )
    Relationships: List[Relationship] = Field(
        ..., description="List of actual relationships linking source and target nodes."
    )
