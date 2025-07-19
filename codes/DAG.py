import json
import os
import networkx as nx
import sys

from collections import deque

def load_json(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def build_dag(json_data):
    G = nx.DiGraph()
    for gate in json_data["gates"]:
        out_net = gate["output"]
        in_nets = gate["inputs"]
        for net in in_nets:
            G.add_edge(net, out_net)
    return G

def find_unvisited_nodes(G):
    return [node for node in G.nodes if G.in_degree(node) == 0 and G.out_degree(node) == 0]

def write_dag_json(G, out_path):
    data = {
        "edges": list(G.edges())
    }
    with open(out_path, 'w') as f:
        json.dump(data, f, indent=2)

def write_unvisited_nodes_json(unvisited, out_path):
    with open(out_path, 'w') as f:
        json.dump({"unvisited_nodes": unvisited}, f, indent=2)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 DAG.py <netlist_json_filename>")
        sys.exit(1)

    filename = sys.argv[1]
    if not filename.endswith(".json"):
        print("Please provide a JSON filename.")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    parsed_dir = os.path.join(script_dir, "parsednetlist")
    output_dir = os.path.join(parsed_dir, "dagoutput")
    os.makedirs(output_dir, exist_ok=True)

    json_path = os.path.join(parsed_dir, filename)
    base_name = os.path.splitext(filename)[0]

    dag_json_path = os.path.join(output_dir, f"{base_name}_dag_edges.json")
    unvisited_json_path = os.path.join(output_dir, f"{base_name}_unvisited_nodes.json")

    data = load_json(json_path)
    G = build_dag(data)

    unvisited = find_unvisited_nodes(G)

    write_dag_json(G, dag_json_path)
    write_unvisited_nodes_json(unvisited, unvisited_json_path)

    print(f"DAG edges written to {dag_json_path}")
    print(f"Unvisited nodes written to {unvisited_json_path}")

if __name__ == "__main__":
    main()
