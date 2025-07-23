import json
import networkx as nx
import matplotlib.pyplot as plt
import os
from networkx.drawing.nx_agraph import to_agraph


def load_dag(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    # Use flattened ports if available
    primary_inputs = data.get("flattened_primary_inputs", data["primary_inputs"])
    primary_outputs = data.get("flattened_primary_outputs", data["primary_outputs"])
    return data['edges'], data['labels'], primary_inputs, primary_outputs


def visualize_graph(json_filename):
    print(f"[INFO] Visualizing: {json_filename}")
    filepath = os.path.join("parsednetlist/dagoutput", json_filename)
    edges, labels, primary_inputs, primary_outputs = load_dag(filepath)

    G = nx.DiGraph()
    G.add_edges_from([(src, dst) for src, dst in edges])

    removed_edges = []
    # Break cycles
    try:
        cycles = list(nx.simple_cycles(G))
        for cycle in cycles:
            if len(cycle) > 1:
                src = cycle[-1]
                dst = cycle[0]
                if G.has_edge(src, dst):
                    G.remove_edge(src, dst)
                    removed_edges.append((src, dst))
                    print(f"[INFO] Removed edge ({src} → {dst}) to break a cycle.")
    except Exception as e:
        print("[ERROR]", e)
        print("[FATAL] Cannot proceed with visualization. Graph is not a DAG.")
        return

    # Use graphviz for hierarchical layout (left to right)
    A = to_agraph(G)
    A.graph_attr.update(rankdir="LR")  # LEFT -> RIGHT
    pos = nx.nx_agraph.graphviz_layout(G, prog='dot')

    node_labels = {}
    node_colors = []

    # Track nodes affected by cycle breaking
    removed_nodes = set()
    for u, v in removed_edges:
        removed_nodes.add(u)
        removed_nodes.add(v)

    for node in G.nodes():
        label = labels.get(node, node)

        if node in removed_nodes:
            color = "#d62728"  # RED
        elif node in primary_inputs:
            color = "#1f77b4"  # BLUE
        elif node in primary_outputs:
            color = "#2ca02c"  # GREEN
        elif '(' in label and ')' in label:
            color = "#ff7f0e"  # ORANGE
        else:
            color = "gray"

        if node in primary_inputs:
            node_labels[node] = f"INPUT → {node}"
        elif node in primary_outputs:
            node_labels[node] = f"{node} → OUTPUT"
        elif '(' in label and ')' in label:
            gate_type = label.split('(')[-1].split(')')[0]
            node_labels[node] = f"{gate_type} → {node}"
        else:
            node_labels[node] = node

        node_colors.append(color)

    plt.figure(figsize=(18, 12))
    nx.draw(
        G, pos,
        with_labels=False,
        node_size=2200,
        node_color=node_colors,
        arrows=True
    )
    nx.draw_networkx_labels(
        G, pos,
        labels=node_labels,
        font_size=10,
        font_family="monospace"
    )

    plt.title(f"Logic Graph: {json_filename}", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig("graph_output.png", dpi=300)
    print("[INFO] Graph saved as graph_output.png")



if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 graph.py <dag_filename.json>")
    else:
        visualize_graph(sys.argv[1])
