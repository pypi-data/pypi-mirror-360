from collections import defaultdict
from typing import Tuple, List, Dict, Any
from atlaz.graph.schema.user_graph_model import Graph

def map_cytoscape_to_graphviz_shape(shape: str) -> str:
    shape_map = {
        'ellipse': 'ellipse',
        'circle': 'octagon',
        'polygon': 'hexagon',
        'egg': 'hexagon',
        'box': 'rectangle',
        'roundrectangle': 'rectangle'
    }
    return shape_map.get(shape, 'ellipse')

def transform_to_cytoscape(graph: Graph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    node_clusters = defaultdict(lambda: {"nodes": [], "shape": None, "color": None})
    for node in graph.nodes:
        graphviz_shape = map_cytoscape_to_graphviz_shape(node.shape)
        key = (graphviz_shape, node.color)
        node_clusters[key]["shape"] = graphviz_shape
        node_clusters[key]["color"] = node.color
        node_clusters[key]["nodes"].append((node.id, node.label))
    nodes_for_create_graph = list(node_clusters.values())
    edge_groups = defaultdict(lambda: defaultdict(list))
    for e in graph.edges:
        key = (e.color, e.arrowhead)
        target_tuple = (e.target, e.label) if e.label else (e.target,)
        edge_groups[key][e.source].append(target_tuple)
    edges_for_create_graph = []
    for (color, arrowhead), connections_dict in edge_groups.items():
        flattened = []
        for source, targets in connections_dict.items():
            for t in targets:
                if len(t) == 2:
                    target, lbl = t
                else:
                    target = t[0]
                    lbl = None
                flattened.append((source, target, lbl))
        edges_for_create_graph.append({
            'color': color,
            'arrowhead': arrowhead,
            'edges': flattened
        })
    return nodes_for_create_graph, edges_for_create_graph, []