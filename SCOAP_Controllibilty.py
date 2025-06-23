# scoap_calculator.py
# ----------------------------------
# Reads 'out.txt' from the Verilog parser and
# computes SCOAP Controllability (CC0/CC1) and Observability (CO).
# Writes results into 'scoap_out.txt'.
#
# Usage:
#   python scoap_calculator.py out.txt
# ----------------------------------

import sys
import re
import math
from collections import defaultdict

def read_netlist(filename):
    """Read lines from out.txt, skip comments/blanks."""
    with open(filename) as f:
        return [
            line.strip() for line in f
            if line.strip() and not line.startswith('#')
        ]

def parse_sections(lines):
    """
    Parse the main sections of out.txt:
      INPUT, OUTPUT, FANOUT, and gate lines like:
        NAND out(g5) in(g3 g4)
    Returns lists: inputs, outputs, fanout_list, gates_list.
    """
    inputs, outputs, fanout_list, gates_list = [], [], [], []
    gate_re = re.compile(r'^(\w+)\s+out\(([^)]+)\)\s+in\(([^)]+)\)$')

    for L in lines:
        parts = L.split()
        if parts[0] == 'INPUT':
            inputs.extend(parts[1:])
        elif parts[0] == 'OUTPUT':
            outputs.extend(parts[1:])
        elif parts[0] == 'FANOUT':
            fanout_list.append(parts)
        else:
            m = gate_re.match(L)
            if m:
                gtype   = m.group(1)
                out_net = m.group(2)
                in_nets = m.group(3).split()
                gates_list.append((gtype, out_net, in_nets))
            # else: ignore unexpected lines
    return inputs, outputs, fanout_list, gates_list

def extract_wires(inputs, outputs, fanout_list, gates_list):
    """Collect all net names from inputs, outputs, fanout and gates."""
    nets = set(inputs) | set(outputs)
    for parts in fanout_list:
        src = parts[1]
        dsts = parts[2:]
        nets.add(src)
        nets.update(dsts)
    for _, out_net, in_nets in gates_list:
        nets.add(out_net)
        nets.update(in_nets)
    return sorted(nets)

def build_controllability(nets, inputs, gates_list):
    """
    Generalized SCOAP controllability for any number of gate inputs
    and varied gate names (e.g. NAND2_X1, AND3X4, etc.).
    """
    # 1) Initialize: PIs = 1, others = ∞
    CC0 = {n: (1 if n in inputs else math.inf) for n in nets}
    CC1 = {n: (1 if n in inputs else math.inf) for n in nets}

    # 2) Iterate until no change (relaxation)
    changed = True
    while changed:
        changed = False
        for gtype, out_net, in_nets in gates_list:
            c0s = [CC0[n] for n in in_nets]
            c1s = [CC1[n] for n in in_nets]
            gt = gtype.upper()

            # Compute new controllabilities per gate type
            if 'NAND' in gt:
                new0 = 1 + min(c0s)        # force 0: one input = 0
                new1 = 1 + sum(c1s)        # force 1: all inputs = 1
            elif 'AND' in gt:
                new0 = 1 + sum(c0s)        # force 0: all inputs = 0
                new1 = 1 + min(c1s)        # force 1: one input = 1
            elif 'NOR' in gt:
                new0 = 1 + sum(c1s)        # force 0: all inputs = 1
                new1 = 1 + min(c0s)        # force 1: one input = 0
            elif 'OR' in gt:
                new0 = 1 + min(c0s)        # force 0: one input = 0
                new1 = 1 + sum(c1s)        # force 1: all inputs = 1
            elif 'XNOR' in gt:
                if len(in_nets) == 2:
                    a0, b0 = c0s; a1, b1 = c1s
                    new0 = 1 + min(a0 + b0, a1 + b1)
                    new1 = 1 + min(a0 + b1, a1 + b0)
                else:
                    # fallback for multi-input: conservative
                    new0 = new1 = 1 + sum(c0s + c1s)
            elif 'XOR' in gt:
                if len(in_nets) == 2:
                    a0, b0 = c0s; a1, b1 = c1s
                    new0 = 1 + min(a0 + b1, a1 + b0)
                    new1 = 1 + min(a0 + b0, a1 + b1)
                else:
                    new0 = new1 = 1 + sum(c0s + c1s)
            else:
                # INV, BUF, and other single-input cells
                new0 = 1 + c1s[0]
                new1 = 1 + c0s[0]

            # Relaxation step
            if new0 < CC0[out_net]:
                CC0[out_net] = new0
                changed = True
            if new1 < CC1[out_net]:
                CC1[out_net] = new1
                changed = True

    # Merge with prefixes for downstream use
    control = {f'CC0_{n}': CC0[n] for n in nets}
    control.update({f'CC1_{n}': CC1[n] for n in nets})
    return control

def build_observability(nets, outputs, fanout_list, control, gates_list):
    """
    Iterative SCOAP observability for any gate fanout and inputs,
    using the computed controllabilities.
    """
    # 1) Initialize: POs = 1, others = ∞
    CO = {n: (1 if n in outputs else math.inf) for n in nets}

    # 2) Build fanout map
    fanout_map = defaultdict(list)
    for parts in fanout_list:
        src = parts[1]
        for dst in parts[2:]:
            fanout_map[src].append(dst)

    # 3) Iterate until convergence
    changed = True
    while changed:
        changed = False

        # a) Nets driving fanouts: CO = min CO of destinations
        for src, dsts in fanout_map.items():
            co_min = min(CO[d] for d in dsts)
            if co_min < CO[src]:
                CO[src] = co_min
                changed = True

        # b) Gate-level propagation inward
        for gtype, out_net, in_nets in gates_list:
            co_out = CO[out_net]
            i1 = in_nets[0]
            i2 = in_nets[1] if len(in_nets) > 1 else in_nets[0]

            c0_i1, c1_i1 = control[f'CC0_{i1}'], control[f'CC1_{i1}']
            c0_i2, c1_i2 = control[f'CC0_{i2}'], control[f'CC1_{i2}']
            gt = gtype.upper()

            if 'AND' in gt or 'NAND' in gt:
                new1 = co_out + c1_i2 + 1
                new2 = co_out + c1_i1 + 1
            elif 'OR' in gt or 'NOR' in gt:
                new1 = co_out + c0_i2 + 1
                new2 = co_out + c0_i1 + 1
            elif 'XOR' in gt or 'XNOR' in gt:
                m = min(c0_i2 + c1_i2, c0_i1 + c1_i1)
                new1 = new2 = co_out + m + 1
            else:
                new1 = new2 = co_out + 1

            if new1 < CO[i1]:
                CO[i1] = new1
                changed = True
            if new2 < CO[i2]:
                CO[i2] = new2
                changed = True

    # Prefix keys for output
    observ = {f'CO_{n}': CO[n] for n in nets}
    return observ

def write_scoap(control, observ, filename='scoap_out.txt'):
    """Write CC0, CC1, and CO tables into a file."""
    with open(filename, 'w') as f:
        # CC0 section
        f.write("--- SCOAP CONTROLLABILITY (CC0) ---\n")
        for k in sorted([k for k in control if k.startswith('CC0_')],
                        key=lambda x: x.split('_',1)[1]):
            f.write(f"{k}: {control[k]}\n")
        f.write("\n")
        # CC1 section
        f.write("--- SCOAP CONTROLLABILITY (CC1) ---\n")
        for k in sorted([k for k in control if k.startswith('CC1_')],
                        key=lambda x: x.split('_',1)[1]):
            f.write(f"{k}: {control[k]}\n")
        f.write("\n")
        # CO section
        f.write("--- SCOAP OBSERVABILITY (CO) ---\n")
        for k in sorted(observ.keys(), key=lambda x: x.split('_',1)[1]):
            f.write(f"{k}: {observ[k]}\n")

    print(f"SCOAP results written to {filename}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python scoap_calculator.py out.txt")
        sys.exit(1)

    lines = read_netlist(sys.argv[1])
    inputs, outputs, fanout_list, gates_list = parse_sections(lines)
    nets = extract_wires(inputs, outputs, fanout_list, gates_list)
    control = build_controllability(nets, inputs, gates_list)
    observ  = build_observability(nets, outputs, fanout_list, control, gates_list)
    write_scoap(control, observ, 'scoap_out.txt')
