import json
import os
import networkx as nx
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


def find_fanouts(G):
    return [node for node in G.nodes if G.out_degree(node) > 1]

def find_reconvergences(G):
    return [node for node in G.nodes if G.in_degree(node) > 1]

def bfs_paths(G, start, end, max_depth=10):
    paths = []
    queue = deque([(start, [start])])
    while queue:
        (node, path) = queue.popleft()
        if node == end:
            paths.append(path)
        elif len(path) < max_depth:
            for next_node in G.successors(node):
                if next_node not in path:
                    queue.append((next_node, path + [next_node]))
    return paths

def write_unvisited_nodes(G, out_path):
    unvisited = [node for node in G.nodes if G.in_degree(node) == 0 and G.out_degree(node) == 0]
    with open(out_path, 'w') as f:
        for node in unvisited:
            f.write(f"{node}\n")

def write_fanout_reconvergence_paths(G, fanouts, reconvergences, out_path):
    with open(out_path, 'w') as f:
        for f_node in fanouts:
            for r_node in reconvergences:
                if nx.has_path(G, f_node, r_node):
                    paths = bfs_paths(G, f_node, r_node)
                    for path in paths:
                        f.write(f"Fanout: {f_node}, Reconvergence: {r_node}, Path: {' -> '.join(path)}\n")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "scoap_out.json")
    unvisited_file = os.path.join(script_dir, "unvisited_nodes.txt")
    fanout_path_file = os.path.join(script_dir, "fanout_reconvergence_paths.txt")

    data = load_json(json_path)
    G = build_dag(data)

    fanouts = find_fanouts(G)
    reconvergences = find_reconvergences(G)

    write_unvisited_nodes(G, unvisited_file)
    write_fanout_reconvergence_paths(G, fanouts, reconvergences, fanout_path_file)

    print("Unvisited nodes written to unvisited_nodes.txt")
    print("Fanout and reconvergence paths written to fanout_reconvergence_paths.txt")

if __name__ == "__main__":
    main()
