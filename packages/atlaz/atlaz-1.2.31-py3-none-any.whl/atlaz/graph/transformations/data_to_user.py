# src/transformations/graphs.py
from typing import Dict, List, Optional, Set, Tuple
from atlaz.graph.schema.user_graph_model import Graph, Node, Edge, Category

def transform_graph_to_user(
    start_object: dict,
    text: str,
    ignore_ids: Optional[List[int]] = None,
) -> dict:
    """
    Transforms the input graph object into a dictionary compatible with the Pydantic Graph schema,
    excluding taxonomy and relationship nodes, color-coding entity nodes by their TaxonomyID, and
    removing transitive edges (A->C) for relationships with type relationships whenever there's
    a one-hop path A->B->C.

    Additionally:
      - Now uses the 'Motivation' field to populate the 'info' key instead of the text snippet.
      - The text snippet from 'TextSource' is placed into a new 'references' list.
    """
    if ignore_ids is None:
        ignore_ids = []
    entity_ids = {
        e["ID"]
        for e in start_object.get("Entities", [])
        if e["ID"] not in ignore_ids
    }
    relationship_entity_map: Dict[int, dict] = {}
    for re_obj in start_object.get("RelationshipEntities", []):
        re_id = re_obj["ID"]
        if re_id in ignore_ids:
            continue
        relationship_entity_map[re_id] = re_obj
    category_mappings = {
        "Entity": {"shape": "ellipse", "color": "lightblue"},
    }
    default_colors = ["lightgreen", "lightblue", "lightyellow", "orange", "pink", "lime"]
    default_shapes = ["ellipse", "circle", "polygon", "box", "egg", "diamond"]
    taxonomy_color_map: Dict[int, str] = {}
    taxonomy_shape_map: Dict[int, str] = {}
    categories: List[Category] = []
    categories.append(Category(name="Entity", color=category_mappings["Entity"]["color"]))
    nodes: List[Node] = []
    for entity in start_object.get("Entities", []):
        e_id = entity["ID"]
        if e_id not in entity_ids:
            continue
        t_id = 1
        color = taxonomy_color_map.get(t_id, category_mappings["Entity"]["color"])
        shape = taxonomy_shape_map.get(t_id, category_mappings["Entity"]["shape"])
        info_from_motivation = entity.get("Motivation") or entity.get("Definition", "")
        references: List[str] = []
        text_source = entity.get("TextSource")
        if type(text_source) == str:
            references = [text_source]
        node = Node(
            id=str(e_id),
            label=entity["Name"],
            color=color,
            shape=shape,
            info=info_from_motivation,
            references=references
        )
        nodes.append(node)
    edges_non_5: List[Tuple[dict, dict]] = []
    edges_5: List[Tuple[dict, dict]] = []
    for rel in start_object.get("Relationships", []):
        s_id = rel["SourceNodeID"]
        t_id = rel["TargetNodeID"]
        re_id = rel["EntityID"]
        if re_id in ignore_ids:
            continue
        rel_entity = relationship_entity_map.get(re_id)
        if not rel_entity:
            continue
        if s_id not in entity_ids or t_id not in entity_ids:
            continue
        if rel_entity['Name'] == 'Is A Type Of':
            edges_5.append((rel, rel_entity))
        else:
            edges_non_5.append((rel, rel_entity))
    adjacency_5: Dict[int, Set[int]] = {}
    for (rel, _) in edges_5:
        s = rel["SourceNodeID"]
        t = rel["TargetNodeID"]
        adjacency_5.setdefault(s, set()).add(t)
    final_edges_5: List[Tuple[dict, dict]] = []
    for (rel, rel_entity) in edges_5:
        s = rel["SourceNodeID"]
        t = rel["TargetNodeID"]
        any_intermediate = False
        if s in adjacency_5:
            for b in adjacency_5[s]:
                if b == t:
                    continue
                if b in adjacency_5 and t in adjacency_5[b]:
                    any_intermediate = True
                    break
        if not any_intermediate:
            final_edges_5.append((rel, rel_entity))

    def build_edge_object(rel: dict, rel_entity: dict) -> Edge:
        if "Type" in rel_entity["Name"]:
            edge_type = "subtype"
        else:
            edge_type = "other"
        arrowhead = "normal" if edge_type == "subtype" else "diamond"
        info_from_motivation = rel.get("Motivation", "")
        references: List[str] = []
        text_source = rel.get("TextSource", "")
        if type(text_source) == str:
            references = [text_source]
        if edge_type == "subtype":
            return Edge(
                source=str(rel["TargetNodeID"]),
                target=str(rel["SourceNodeID"]),
                type=edge_type,
                color="black",
                arrowhead=arrowhead,
                label=rel_entity["Name"],
                info=info_from_motivation,
                references=references
            )
        else:
            return Edge(
                source=str(rel["SourceNodeID"]),
                target=str(rel["TargetNodeID"]),
                type=edge_type,
                color="black",
                arrowhead=arrowhead,
                label=rel_entity["Name"],
                info=info_from_motivation,
                references=references
            )
    final_edges: List[Edge] = []
    for (rel, rel_entity) in edges_non_5:
        final_edges.append(build_edge_object(rel, rel_entity))
    for (rel, rel_entity) in final_edges_5:
        final_edges.append(build_edge_object(rel, rel_entity))
    graph_dict = {
        "nodes": [node.dict() for node in nodes],
        "edges": [edge.dict() for edge in final_edges],
        "categories": [cat.dict() for cat in categories],
    }
    try:
        Graph(**graph_dict)
    except Exception as e:
        raise ValueError(f"Validation error: {e}")
    return graph_dict