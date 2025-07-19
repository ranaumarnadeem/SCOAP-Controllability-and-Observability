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

def visualize_dag(dag_data, title="Gate-Level DAG", output_file=None):
    G = nx.DiGraph()
    
    edges = dag_data["edges"]
    labels = dag_data.get("labels", {})

    G.add_edges_from(edges)

    # Node label mapping
    node_labels = {node: labels.get(node, node) for node in G.nodes}

    # Layout
    pos = nx.spring_layout(G, k=0.5, iterations=100)

    plt.figure(figsize=(18, 12))
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue')
    nx.draw_networkx_edges(G, pos, arrows=True, edge_color='gray')
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8)

    plt.title(title)
    plt.axis('off')
    plt.tight_layout()

    # Save if filename is given
    if output_file:
        plt.savefig(output_file, dpi=300)
        print(f"[INFO] DAG image saved as: {output_file}")

    # Show only if in interactive environment
    try:
        plt.show()
    except:
        print("[WARN] Cannot display plot in this environment.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 graph.py <json_filename>")
        sys.exit(1)

    json_file = sys.argv[1]
    dag_data = load_dag_json(json_file)

    # Get base name for output image
    base_name = os.path.splitext(json_file)[0]
    output_image = os.path.join("parsednetlist", "dagoutput", f"{base_name}_dag.png")

    visualize_dag(dag_data, title=f"DAG: {json_file}", output_file=output_image)

if __name__ == "__main__":
    main()
