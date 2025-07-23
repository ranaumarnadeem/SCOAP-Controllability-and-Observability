import json
import os
import re
import sys

def parse_netlist_txt(txt_path):
    gates = []
    primary_inputs = []
    primary_outputs = []

    with open(txt_path, 'r') as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            # Capture primary inputs
            if line.startswith('INPUT'):
                primary_inputs.extend(line.replace('INPUT', '').strip().split())
                continue

            # Capture primary outputs
            if line.startswith('OUTPUT'):
                primary_outputs.extend(line.replace('OUTPUT', '').strip().split())
                continue

            # Match gates
            match = re.match(r'(\w+)\s+out\((\S+)\)\s+in\((.*?)\)', line)
            if match:
                gate_type = match.group(1)
                output = match.group(2)
                inputs = match.group(3).split()

                gates.append({
                    "type": gate_type,
                    "output": output,
                    "inputs": inputs
                })

    return {
        "primary_inputs": primary_inputs,
        "primary_outputs": primary_outputs,
        "gates": gates
    }

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 convert_txt_to_json.py <filename.txt>")
        return

    input_name = sys.argv[1]
    if not input_name.endswith('.txt'):
        print("Error: Input file must have a .txt extension.")
        return

    base_dir = os.path.join(os.path.dirname(__file__), 'parsednetlist')
    input_path = os.path.join(base_dir, input_name)

    if not os.path.exists(input_path):
        print(f"[!] File not found: {input_path}")
        return

    output_name = input_name.replace('.txt', '.json')
    output_path = os.path.join(base_dir, output_name)

    data = parse_netlist_txt(input_path)

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"[+] Parsed '{input_name}' and saved JSON to '{output_name}' in 'parsednetlist/'")

if __name__ == "__main__":
    main()
