import json
import os
import sys
import pygraphviz as pgv

def load_dag(json_file_path):
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    edges = data['edges']
    labels = data['labels']
    primary_inputs = data.get("flattened_primary_inputs", data.get("primary_inputs", []))
    primary_outputs = data.get("flattened_primary_outputs", data.get("primary_outputs", []))

    return edges, labels, primary_inputs, primary_outputs


def gate_centric_label(label):
    try:
        parts = label.split()
        gate_type = parts[0]
        out_net = parts[1].split('(')[1][:-1]
        in_nets = parts[2].split('(')[1][:-1].split()
        return f"{gate_type}({', '.join(in_nets)}) → {out_net}"
    except:
        return label


def visualize_gate_graph(json_filename):
    # Locate directories relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dag_dir = os.path.join(script_dir, 'dagoutput')
    graph_dir = os.path.join(script_dir, 'graphs')
    os.makedirs(graph_dir, exist_ok=True)

    json_path = os.path.join(dag_dir, json_filename)
    if not os.path.exists(json_path):
        print(f"[✗] File not found: {json_path}")
        sys.exit(1)

    edges, raw_labels, primary_inputs, primary_outputs = load_dag(json_path)

    G = pgv.AGraph(strict=False, directed=True)
    G.graph_attr.update(rankdir="LR", splines="true", nodesep="0.5", ranksep="1")

    for node, raw_label in raw_labels.items():
        label = gate_centric_label(raw_label)
        if node in primary_inputs:
            G.add_node(node, label=node, shape="box", style="filled", fillcolor="#aec7e8")
        elif node in primary_outputs:
            G.add_node(node, label=node, shape="box", style="filled", fillcolor="#98df8a")
        elif '(' in label:
            G.add_node(node, label=label, shape="ellipse", style="filled", fillcolor="#ffbb78")
        else:
            G.add_node(node, label=label, shape="ellipse", style="filled", fillcolor="#d3d3d3")

    for u, v in edges:
        G.add_edge(u, v)

    png_name = os.path.splitext(json_filename)[0] + "_graph.png"
    output_path = os.path.join(graph_dir, png_name)

    G.layout(prog="dot")
    G.draw(output_path)
    print(f"[✓] Graph saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 graph.py <dag_filename.json>")
    else:
        visualize_gate_graph(sys.argv[1])
