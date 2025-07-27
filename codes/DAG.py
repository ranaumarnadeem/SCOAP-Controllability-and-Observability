import json
import os
import sys
import re

"""
dag.py
Reads parsed netlist JSON from codes/parsednetlist/<design>.json
Writes DAG JSON to codes/dagoutput/<design>_dag.json
Usage:
  cd codes
  python3 dag.py <design>.json
"""

def load_parsed_netlist(json_file):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parsed_dir = os.path.join(script_dir, 'parsednetlist')
    path = os.path.join(parsed_dir, json_file)
    if not os.path.exists(path):
        print(f"[ERROR] Parsed netlist not found: {path}")
        sys.exit(1)
    with open(path, 'r') as f:
        return json.load(f)


def build_dag(gates):
    edges = []
    labels = {}
    for gate in gates:
        gate_type = gate.get('type')
        output = gate.get('output')
        inputs = gate.get('inputs', [])
        # skip UNCONNECTED nets
        if not output or output.startswith('UNCONNECTED'):
            continue
        # label this node
        labels[output] = f"{output} ({gate_type})"
        # build edges
        for inp in inputs:
            edges.append([inp, output])
            if inp not in labels:
                labels[inp] = inp
    return edges, labels


def save_dag_json(dag_data, input_filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, 'dagoutput')
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(input_filename))[0]
    output_path = os.path.join(output_dir, f"{base}_dag.json")
    with open(output_path, 'w') as f:
        json.dump(dag_data, f, indent=2)
    print(f"[✓] DAG saved to {output_path}")


def flatten_signal(signal):
    m = re.match(r'(.+)\[(\d+):(\d+)\]', signal)
    if m:
        name, hi, lo = m.group(1), int(m.group(2)), int(m.group(3))
        step = 1 if hi >= lo else -1
        return [f"{name}[{i}]" for i in range(hi, lo - step, -step)]
    return [signal]


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 dag.py <design>.json>")
        sys.exit(1)
    json_file = sys.argv[1]

    data = load_parsed_netlist(json_file)
    gates = data.get('gates')
    if gates is None:
        print("[ERROR] 'gates' key not found in parsed netlist")
        sys.exit(1)

    edges, labels = build_dag(gates)

    # handle primary inputs/outputs
    raw_inputs = data.get('primary_inputs', [])
    raw_outputs = data.get('primary_outputs', [])
    flat_inputs = []
    for sig in raw_inputs:
        flat_inputs.extend(flatten_signal(sig))
    flat_outputs = []
    for sig in raw_outputs:
        flat_outputs.extend(flatten_signal(sig))

    dag_data = {
        'edges': edges,
        'labels': labels,
        'primary_inputs': flat_inputs,
        'primary_outputs': flat_outputs
    }

    save_dag_json(dag_data, json_file)

if __name__ == '__main__':
    main()
