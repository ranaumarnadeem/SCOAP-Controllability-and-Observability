import json
import os
import sys
import pygraphviz as pgv


def load_dag(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    edges = data['edges']
    labels = data['labels']
    primary_inputs = data.get("flattened_primary_inputs", data["primary_inputs"])
    primary_outputs = data.get("flattened_primary_outputs", data["primary_outputs"])

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
    filepath = os.path.join("parsednetlist/dagoutput", json_filename)
    edges, raw_labels, primary_inputs, primary_outputs = load_dag(filepath)

    G = pgv.AGraph(strict=False, directed=True)
    G.graph_attr.update(rankdir="LR", splines="true", nodesep="0.5", ranksep="1")

    for node in raw_labels:
        label = gate_centric_label(raw_labels[node])
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

    output_path = "graph_output.png"
    G.layout(prog="dot")
    G.draw(output_path)
    print(f"[✓] Graph saved as {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 graph.py <dag_filename.json>")
    else:
        visualize_gate_graph(sys.argv[1])
