from typing import Dict

def map_json_to_extensive_graph(input_data: Dict) -> Dict:
    """
    Transforms an input dict (with keys "Entities", "RelationshipEntities",
    and "Relationships") into a dict validated by Graph(**...) 
    under the OutputPydanticSchema.
    
    Keeps the original IDs from the input, converted to strings 
    for the Pydantic Node/Edge schemas. 
    Special logic: if the relationship label == "Is A Type Of",
    we set edge["type"] = "subtype"; otherwise "other".
    """
    entities_lookup = {}
    rel_entities_lookup = {}
    nodes = []
    for entity in input_data.get("Entities", []):
        eid = entity["ID"]
        name = entity["Name"]
        definition = entity["Definition"]
        entities_lookup[eid] = name
        node = {
            "id": str(eid),
            "label": name,
            "color": "#1f77b4",
            "shape": "ellipse",
            "info": definition,
            "references": []
        }
        nodes.append(node)
    for rel_entity in input_data.get("RelationshipEntities", []):
        rid = rel_entity["ID"]
        name = rel_entity["Name"]
        definition = rel_entity["Definition"]
        transitive = rel_entity["Transitive"]
        bidirectional = rel_entity["Bidirectional"]
        rel_entities_lookup[rid] = name
        info_str = (
            f"{definition}\n"
            f"Transitive: {transitive}, Bidirectional: {bidirectional}"
        )
        node = {
            "id": str(rid),
            "label": name,
            "color": "#ff7f0e",
            "shape": "diamond",
            "info": info_str,
            "references": []
        }
        nodes.append(node)
    edges = []
    for rel in input_data.get("Relationships", []):
        relationship_type_id = rel["EntityID"]
        relationship_label = rel_entities_lookup.get(relationship_type_id, "unknown-rel")
        source_str = str(rel["SourceNodeID"])
        target_str = str(rel["TargetNodeID"])
        if relationship_label == "Is A Type Of":
            edge_type = "subtype"
        else:
            edge_type = "other"
        edge = {
            "source": source_str,
            "target": target_str,
            "type": edge_type,
            "color": "#555555",
            "arrowhead": "normal",
            "label": relationship_label,
            "info": rel["Motivation"],
            "references": []
        }
        edges.append(edge)
    categories = [
        {
            "name": "Entity",
            "color": "#1f77b4",
        },
        {
            "name": "RelationshipEntity",
            "color": "#ff7f0e",
        }
    ]
    graph_dict = {
        "nodes": nodes,
        "edges": edges,
        "categories": categories
    }
    return graph_dict