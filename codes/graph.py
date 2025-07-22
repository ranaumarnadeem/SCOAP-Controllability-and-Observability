import json
import networkx as nx
import matplotlib.pyplot as plt
import os
from networkx.drawing.nx_agraph import graphviz_layout


def load_dag(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data['edges'], data['labels'], data['primary_inputs'], data['primary_outputs']


def visualize_graph(json_filename):
    print(f"[INFO] Visualizing: {json_filename}")
    filepath = os.path.join("parsednetlist/dagoutput", json_filename)
    edges, labels, primary_inputs, primary_outputs = load_dag(filepath)

    G = nx.DiGraph()
    G.add_edges_from([(src, dst) for src, dst in edges])

    # Detect and remove one edge per cycle (for visualization only)
    try:
        cycles = list(nx.simple_cycles(G))
        for cycle in cycles:
            if len(cycle) > 1:
                src = cycle[-1]
                dst = cycle[0]
                if G.has_edge(src, dst):
                    G.remove_edge(src, dst)
                    print(f"[INFO] Removed edge ({src} → {dst}) to break a cycle for visualization.")
    except Exception as e:
        print("[ERROR]", e)
        print("[FATAL] Cannot proceed with visualization. Graph is not a DAG.")
        return

    pos = graphviz_layout(G, prog='dot')

    node_labels = {}
    node_colors = []

    for node in G.nodes():
        label = labels.get(node, node)

        if node in primary_inputs:
            node_labels[node] = f"INPUT → {node}"
            node_colors.append("#1f77b4")  # Blue for inputs
        elif node in primary_outputs:
            node_labels[node] = f"{node} → OUTPUT"
            node_colors.append("#2ca02c")  # Green for outputs
        elif '(' in label and ')' in label:
            gate_type = label.split('(')[-1].split(')')[0]
            node_labels[node] = f"{gate_type} → {node}"
            node_colors.append("#ff7f0e")  # Orange for gates
        else:
            node_labels[node] = node
            node_colors.append("gray")

    plt.figure(figsize=(16, 10))
    nx.draw(G, pos, with_labels=False, node_size=2200, node_color=node_colors, arrows=True)
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, font_family="monospace")

    plt.title(f"Logic Graph: {json_filename}", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 graph.py <dag_filename.json>")
    else:
        visualize_graph(sys.argv[1])
