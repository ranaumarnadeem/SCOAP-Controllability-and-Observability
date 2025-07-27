
# -------------------------------
# Reads DAG JSON from codes/dagoutput/<design>_dag.json
# Writes reconvergence JSON to codes/reconvergence/<design>_reconv.json
# -------------------------------

import json
import os
import sys
import networkx as nx
from itertools import combinations
from collections import deque


def load_dag_json(filepath):
    if not os.path.exists(filepath):
        print(f"[ERROR] DAG JSON not found: {filepath}")
        sys.exit(1)
    with open(filepath, 'r') as f:
        return json.load(f)


def build_dag_graph(dag_data):
    G = nx.DiGraph()
    G.add_edges_from(dag_data['edges'])
    return G


def break_cycles(G):
    # Remove back-edges until acyclic
    try:
        while True:
            cycle = nx.find_cycle(G, orientation='original')
            u, v, _ = cycle[-1]
            G.remove_edge(u, v)
            print(f"[WARN] Removed cycle edge {u} -> {v}")
    except nx.NetworkXNoCycle:
        pass


def find_fanout_points(G):
    return [n for n in G.nodes if G.out_degree(n) > 1]


def bfs_path(G, source, target, max_depth=20):
    queue = deque([[source]])
    while queue:
        path = queue.popleft()
        if path[-1] == target:
            return path
        if len(path) >= max_depth:
            continue
        for nxt in G.successors(path[-1]):
            if nxt not in path:
                queue.append(path + [nxt])
    return None


def find_reconvergences(G):
    fanouts = find_fanout_points(G)
    results = []
    for site in G.nodes:
        sources = [f for f in fanouts if nx.has_path(G, f, site)]
        for a, b in combinations(sources, 2):
            p1 = bfs_path(G, a, site)
            p2 = bfs_path(G, b, site)
            if p1 and p2:
                if set(p1[1:-1]).isdisjoint(p2[1:-1]):
                    results.append({
                        'site': site,
                        'branch1': a,
                        'branch2': b,
                        'path1': p1,
                        'path2': p2
                    })
    return results


def save_reconvergence(data, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"[✓] Reconvergence saved to {out_path}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 reconverge.py <design>_dag.json")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    dag_dir = os.path.join(script_dir, 'dagoutput')
    reconv_dir = os.path.join(script_dir, 'reconvergence')

    dag_file = sys.argv[1]
    base = os.path.splitext(dag_file)[0]

    dag_path = os.path.join(dag_dir, dag_file)
    out_path = os.path.join(reconv_dir, f"{base}_reconv.json")

    dag_data = load_dag_json(dag_path)
    G = build_dag_graph(dag_data)
    break_cycles(G)
    reconv = find_reconvergences(G)
    save_reconvergence(reconv, out_path)

if __name__ == '__main__':
    main()
