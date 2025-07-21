import json
import os
import sys

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

        # Add label for output node
        labels[output] = f"{output} ({gate_type})"

        for input_signal in inputs:
            edges.append([input_signal, output])
            # Add label for input if not already added
            if input_signal not in labels:
                labels[input_signal] = input_signal

    return {"edges": edges, "labels": labels}

def save_dag_json(dag_data, input_filename):
    name = os.path.splitext(os.path.basename(input_filename))[0]
    output_dir = os.path.join("parsednetlist", "dagoutput")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{name}_dag.json")
    with open(output_path, 'w') as f:
        json.dump(dag_data, f, indent=2)
    print(f"[INFO] DAG saved to {output_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 DAG.py <parsed_netlist.json>")
        sys.exit(1)

    json_file = sys.argv[1]
    netlist = load_parsed_netlist(json_file)
    if "gates" not in netlist:
        print("[ERROR] Invalid netlist format. Key 'gates' not found.")
        sys.exit(1)

    dag = build_dag(netlist["gates"])
    save_dag_json(dag, json_file)

if __name__ == "__main__":
    main()
