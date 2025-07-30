from matplotlib import pyplot as plt
import igraph as ig
from collections import defaultdict


def iplot(graph, target=None, layout='auto', visual_style=None):
    # print('iplot')
    # print(graph.vs['name'])
    default_style = {
        "vertex_label": graph.vs["name"] if "name" in graph.vs.attributes() else None,
        # 2 decimal places for edge labels
        "edge_label": ["{:.2f}".format(weight) for weight in graph.es["weight"]] if "weight" in graph.es.attributes() else None,
        "bbox": (300, 300),  # You can adjust the size as needed
        "margin": 20,
        # Add more default styling options here if desired
    }

    if visual_style is not None:
        # Ensure that visual_style is a dictionary
        if not isinstance(visual_style, dict):
            raise TypeError("visual_style must be a dictionary of visual style attributes.")
        # Update the default style with user-provided style
        default_style.update(visual_style)

    if target is None:
        target = plt.subplots()[1]
    ig.plot(graph, layout=layout, target=target, **default_style)

def pyviz(graph, notebook=False, output_file='graph.html'):
    try:
        from pyvis.network import Network
    except ImportError:
        raise ImportError(
            "pyvis is required for interactive graph visualization. "
            "Install it with: pip install 'ciga[visualization]' or pip install pyvis"
        )
    
    net = Network(height="750px", width="100%", notebook=notebook, directed=graph.is_directed())

    node_labels = graph.vs["name"] if "name" in graph.vs.attributes() else [str(v.index) for v in graph.vs]

    # Add nodes with custom attributes
    for i, label in enumerate(node_labels):
        net.add_node(i, label=label, color='red', size=20)

    # Add edges with custom attributes
    edge_weights = graph.es["weight"] if "weight" in graph.es.attributes() else [1]*len(graph.es)
    for e, w in zip(graph.es, edge_weights):
        if e.source != e.target:  # Skip self-loops
            net.add_edge(e.source, e.target, value=w, label=str(w), width=2)

    # Enable physics for better layout
    net.toggle_physics(True)

    # Provide user controls
    net.show_buttons()

    # Generate and display the interactive visualization
    net.show(output_file, notebook=notebook)
