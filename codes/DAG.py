import json
import os
import sys
import networkx as nx
import matplotlib.pyplot as plt

def load_dag_json(json_file):
    json_dir = os.path.join("parsednetlist", "dagoutput")
    json_path = os.path.join(json_dir, json_file)

    if not os.path.exists(json_path):
        print(f"[ERROR] JSON file not found at: {json_path}")
        sys.exit(1)

    with open(json_path, 'r') as f:
        return json.load(f)

def categorize_node(node_name):
    if node_name.startswith("in["):
        return "input"
    elif node_name.startswith("out[") or node_name in ["valid"]:
        return "output"
    else:
        return "gate"

def visualize_dag(dag_data, title="Gate-Level DAG", output_file=None):
    try:
        from networkx.drawing.nx_agraph import graphviz_layout
        pos = graphviz_layout(nx.DiGraph(dag_data["edges"]), prog="dot")
    except ImportError:
        print("[WARN] pygraphviz not installed. Using spring layout.")
        pos = nx.spring_layout(nx.DiGraph(dag_data["edges"]), k=0.5, iterations=100)

    G = nx.DiGraph()
    G.add_edges_from(dag_data["edges"])
    labels = dag_data.get("labels", {})
    node_labels = {node: labels.get(node, node) for node in G.nodes}

    # Assign node colors
    color_map = []
    for node in G.nodes:
        cat = categorize_node(node)
        if cat == "input":
            color_map.append("#90ee90")  # light green
        elif cat == "output":
            color_map.append("#ff7f7f")  # light red
        else:
            color_map.append("#add8e6")  # light blue

    plt.figure(figsize=(18, 12), facecolor='white')
    nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=700, edgecolors='black', linewidths=0.5)
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowstyle='-|>', connectionstyle='arc3,rad=0.1')
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=7)

    plt.title(title)
    plt.axis('off')
    plt.tight_layout()

    if output_file:
        plt.savefig(output_file, dpi=300, facecolor='white')
        print(f"[INFO] DAG image saved as: {output_file}")

    try:
        plt.show()
    except:
        print("[WARN] Plot could not be displayed in this environment.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 graph.py <json_filename>")
        sys.exit(1)

    json_file = sys.argv[1]
    dag_data = load_dag_json(json_file)

    base = os.path.splitext(json_file)[0]
    out_file = os.path.join("parsednetlist", "dagoutput", f"{base}_dag.png")

    visualize_dag(dag_data, f"DAG: {json_file}", out_file)

if __name__ == "__main__":
    main()
