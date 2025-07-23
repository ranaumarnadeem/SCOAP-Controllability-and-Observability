import json
import os
import sys
import re

def load_parsed_netlist(json_file):
    path = os.path.join("parsednetlist", json_file)
    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}")
        sys.exit(1)
    with open(path, 'r') as f:
        return json.load(f)

def build_dag(gates):
    edges = []
    labels = {}

    for gate in gates:
        gate_type = gate.get("type")
        output = gate.get("output")
        inputs = gate.get("inputs", [])

        if output.startswith("UNCONNECTED"):
            continue  # skip unconnected outputs

        labels[output] = f"{output} ({gate_type})"

        for input_signal in inputs:
            edges.append([input_signal, output])
            if input_signal not in labels:
                labels[input_signal] = input_signal

    return edges, labels

def save_dag_json(dag_data, input_filename):
    name = os.path.splitext(os.path.basename(input_filename))[0]
    output_dir = os.path.join("parsednetlist", "dagoutput")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{name}_dag.json")
    with open(output_path, 'w') as f:
        json.dump(dag_data, f, indent=2)
    print(f"[INFO] DAG saved to {output_path}")


def flatten_signal(signal):
    """Expands bus signals like A[3:0] into A[3], A[2], A[1], A[0]"""
    match = re.match(r'(\w+)\[(\d+):(\d+)\]', signal)
    if match:
        name = match.group(1)
        high = int(match.group(2))
        low = int(match.group(3))
        return [f"{name}[{i}]" for i in range(high, low - 1, -1)]
    else:
        return [signal]

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 DAG.py <parsed_netlist.json>")
        sys.exit(1)

    json_file = sys.argv[1]
    netlist = load_parsed_netlist(json_file)

    if "gates" not in netlist:
        print("[ERROR] Invalid netlist format. Key 'gates' not found.")
        sys.exit(1)

    edges, labels = build_dag(netlist["gates"])

    # Flatten primary inputs/outputs
    raw_inputs = netlist.get("primary_inputs", [])
    raw_outputs = netlist.get("primary_outputs", [])

    flattened_inputs = []
    for signal in raw_inputs:
        flattened_inputs.extend(flatten_signal(signal))

    flattened_outputs = []
    for signal in raw_outputs:
        flattened_outputs.extend(flatten_signal(signal))

    dag_data = {
        "edges": edges,
        "labels": labels,
        "primary_inputs": flattened_inputs,
        "primary_outputs": flattened_outputs
    }

    save_dag_json(dag_data, json_file)

if __name__ == "__main__":
    main()
