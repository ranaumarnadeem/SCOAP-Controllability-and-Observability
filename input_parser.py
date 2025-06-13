import argparse
import re

# Supported components
GATES = {"AND", "OR", "NAND", "NOR", "XOR", "XNOR"}
FLIPFLOPS = {"DFF", "TFF", "JKFF", "SRFF"}
SPECIAL = {"INPUT", "OUTPUT", "FANOUT"}

def parse_netlist(input_path, output_path):
    gate_list = []
    inputs = []
    outputs = []
    fanouts = []
    ff_list = []
    scan_muxes = []
    unknown = []

    # Regular expression to extract pins from parentheses
    pin_pattern = re.compile(r'\(([^)]+)\)')

    with open(input_path, 'r') as file:
        for line in file:
            line = line.strip().rstrip(';')
            if not line or line.startswith("#"):
                continue

            tokens = line.split()
            comp = tokens[0].upper()

            # Handle gate components with parentheses
            if comp in GATES and len(tokens) >= 2:
                # Check if pins are in parentheses format
                if '(' in tokens[1]:
                    # Extract content from parentheses
                    pin_match = pin_pattern.search(' '.join(tokens[1:]))
                    if pin_match:
                        pins = pin_match.group(1).split(',')
                        if len(pins) >= 3:  # Output + at least 2 inputs
                            gate_list.append((tokens[0], pins[0].strip(), [p.strip() for p in pins[1:]]))
                        else:
                            print(f"Warning: Invalid gate pins -> {line}")
                    else:
                        print(f"Warning: No parentheses match -> {line}")
                # Handle simple space-separated format
                elif len(tokens) >= 4:
                    gate_list.append((tokens[0], tokens[1], tokens[2:]))
                else:
                    print(f"Warning: Invalid gate line -> {line}")

            # Handle flip-flops
            elif comp in FLIPFLOPS and len(tokens) >= 2:
                # Check if pins are in parentheses format
                if '(' in tokens[1]:
                    pin_match = pin_pattern.search(' '.join(tokens[1:]))
                    if pin_match:
                        pins = pin_match.group(1).split(',')
                        if len(pins) >= 2:  # Output + at least 1 input
                            ff_list.append((tokens[0], pins[0].strip(), [p.strip() for p in pins[1:]]))
                        else:
                            print(f"Warning: Invalid FF pins -> {line}")
                # Handle simple format
                elif len(tokens) >= 3:
                    ff_list.append((tokens[0], tokens[1], tokens[2:]))
                else:
                    print(f"Warning: Invalid FF line -> {line}")

            # Handle other components
            elif comp == "INPUT":
                inputs.extend([t.rstrip(',') for t in tokens[1:]])

            elif comp == "OUTPUT":
                outputs.extend([t.rstrip(',') for t in tokens[1:]])

            elif comp == "FANOUT":
                if len(tokens) >= 3:
                    fanouts.append((tokens[1], [t.rstrip(',') for t in tokens[2:]]))
                else:
                    print(f"Warning: Invalid fanout line -> {line}")

            elif comp.startswith("SCANMUX"):
                if len(tokens) >= 3:
                    scan_muxes.append((tokens[0], tokens[1], tokens[2:]))
                else:
                    print(f"Warning: Invalid scanmux line -> {line}")

            else:
                unknown.append(line)

    # (Rest of the output writing code remains the same)
    # [Keep the original output writing code here]
    
    # Write the output file (same as original)
    with open(output_path, 'w') as out:
        out.write("=== Parsed Netlist Summary ===\n\n")

        if inputs:
            out.write("Primary Inputs:\n")
            out.write("  " + ", ".join(inputs) + "\n\n")

        if outputs:
            out.write("Primary Outputs:\n")
            out.write("  " + ", ".join(outputs) + "\n\n")

        if gate_list:
            out.write("Logic Gates:\n")
            out.write(f"{'Type':8} {'Output':8} {'Inputs'}\n")
            for gate, outnet, in_nets in gate_list:
                out.write(f"{gate:8} {outnet:8} {', '.join(in_nets)}\n")
            out.write("\n")

        if ff_list:
            out.write("Flip-Flops:\n")
            out.write(f"{'Type':8} {'Output':8} {'Inputs'}\n")
            for ff, outnet, in_nets in ff_list:
                out.write(f"{ff:8} {outnet:8} {', '.join(in_nets)}\n")
            out.write("\n")

        if scan_muxes:
            out.write("Scan MUXes:\n")
            out.write(f"{'Type':12} {'Output':8} {'Inputs'}\n")
            for mux, outnet, in_nets in scan_muxes:
                out.write(f"{mux:12} {outnet:8} {', '.join(in_nets)}\n")
            out.write("\n")

        if fanouts:
            out.write("Fanout Information:\n")
            for src, dests in fanouts:
                out.write(f"  Net {src} fans out to: {', '.join(dests)}\n")
            out.write("\n")

        if unknown:
            out.write("Unknown Lines (Check Syntax or Add Support):\n")
            for line in unknown:
                out.write(f"  {line}\n")
            out.write("\n")

        out.write("=== End of Netlist ===\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Netlist Parser and Formatter")
    parser.add_argument("input_file", help="Input netlist file (e.g. netlist.v or test.txt)")
    parser.add_argument("output_file", help="Output parsed text file")
    args = parser.parse_args()

    parse_netlist(args.input_file, args.output_file)