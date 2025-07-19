import json
import os
import re
import sys

def parse_netlist_txt(txt_path):
    gates = []
    with open(txt_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('INPUT') or line.startswith('OUTPUT'):
                continue

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
    return {"gates": gates}

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
