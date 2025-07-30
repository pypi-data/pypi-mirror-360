from graphviz import Digraph

def spread_edges(list1):
    spread = []
    for a, b_s in list1:
        for b in b_s:
            if isinstance(b, tuple) and len(b) == 2:
                target, label = b
                spread.append((a, target, label))
            else:
                spread.append((a, b, None))
    return spread

def transform_edges(edges):
    return [
        {
            'color': edge_obj.get('color', 'black'),
            'arrowhead': edge_obj.get('arrowhead', 'normal'),
            'edges': spread_edges(edge_obj['connections']),
        }
        for edge_obj in edges
    ]

def create_graph(nodes, edges, clusters, filename):
    dot = Digraph(comment='Knowledge Graph', format='png')
    for cluster in nodes:
        for node_id, node_name in cluster['nodes']:
            dot.node(str(node_id), node_name, shape=cluster['shape'], style='filled', fillcolor=cluster['color'])
    for edge in edges:
        color = edge.get('color', 'black')
        arrowhead = edge.get('arrowhead', 'normal')
        for connection in edge['edges']:
            a, b, label = connection
            if label:
                dot.edge(str(a), str(b), color=color, arrowhead=arrowhead, label=label)
            else:
                dot.edge(str(a), str(b), color=color, arrowhead=arrowhead)
    for cluster in clusters:
        with dot.subgraph(name='cluster_' + cluster['name']) as c:
            c.attr(style='filled', color=cluster['color'])
            for n in cluster['nodes']:
                c.node(str(n))
            c.attr(label=cluster['name'])
    dot.render(filename, view=True, cleanup=True)