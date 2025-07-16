#!/usr/bin/env python3
# scoap_calculator.py
# ----------------------------------
# Reads 'out.txt' from the Verilog parser and
# computes SCOAP Controllability (CC0/CC1) and Observability (CO).
# Writes results into 'scoap_out.txt' (next to this script).
#
# Usage:
#   python scoap_calculator.py path/to/out.txt
# ----------------------------------

import sys
import os
import re
import math
from collections import defaultdict

def expand_vector(signal):
    """Expand vector like in[7:0] into in[7], in[6], …, in[0]."""
    m = re.match(r'^(\w+)\[(\d+):(\d+)\]$', signal)
    if not m:
        return [signal]
    base, msb, lsb = m.group(1), int(m.group(2)), int(m.group(3))
    if msb >= lsb:
        return [f"{base}[{i}]" for i in range(msb, lsb - 1, -1)]
    else:
        return [f"{base}[{i}]" for i in range(msb, lsb + 1)]

def read_netlist(filename):
    """Read all non-blank lines (including those starting with '#')."""
    try:
        with open(filename) as f:
            lines = [line.rstrip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: cannot open '{filename}'", file=sys.stderr)
        sys.exit(1)
    return lines

def parse_sections(lines):
    inputs, outputs = [], []
    fanout_list, gates_list = [], []
    section = None

    gate_re = re.compile(r'^\s*(\w+)\s+out\(\s*([^)]+)\s*\)\s+in\(\s*([^)]+)\s*\)\s*$')

    for lineno, line in enumerate(lines, start=1):
        # detect section by header comment
        if line.startswith('#'):
            if 'Primary Inputs'  in line:
                section = 'INPUT'
            elif 'Primary Outputs' in line:
                section = 'OUTPUT'
            elif 'FAN OUT' in line:
                section = 'FANOUT'
            elif 'Complete Paths' in line:
                section = 'GATES'
            else:
                section = None
            continue

        # summary lines (INPUT, OUTPUT, FANOUT) appear after Complete Paths; skip them
        if section == 'GATES' and (line.startswith('INPUT ') or line.startswith('OUTPUT ') or line.startswith('FANOUT ')):
            continue

        if section == 'INPUT':
            for token in line.split():
                inputs.extend(expand_vector(token))

        elif section == 'OUTPUT':
            for token in line.split():
                outputs.extend(expand_vector(token))

        elif section == 'FANOUT':
            parts = line.split()
            if len(parts) >= 2:
                src = parts[1]
                dsts = parts[2:]
                fanout_list.append((src, dsts))
            else:
                print(f"[WARN] Malformed FANOUT line @{lineno}: '{line}'", file=sys.stderr)

        elif section == 'GATES':
            m = gate_re.match(line)
            if not m:
                print(f"[WARN] Gate line skipped @{lineno}: '{line}'", file=sys.stderr)
            else:
                gtype, out_net, in_list = m.group(1), m.group(2), m.group(3)
                in_nets = in_list.split()
                gates_list.append((gtype, out_net, in_nets))

    # Debug output
    print("=== DEBUG: Parsed Sections ===")
    print(f"Inputs  ({len(inputs)}): {inputs}")
    print(f"Outputs ({len(outputs)}): {outputs}")
    print(f"Fanout  ({len(fanout_list)}): {fanout_list}")
    print(f"Gates   ({len(gates_list)}): {gates_list}")
    return inputs, outputs, fanout_list, gates_list

def extract_wires(inputs, outputs, fanout_list, gates_list):
    nets = set(inputs) | set(outputs)
    for src, dsts in fanout_list:
        nets.add(src)
        nets.update(dsts)
    for _, out_net, in_nets in gates_list:
        nets.add(out_net)
        nets.update(in_nets)
    return sorted(nets)

def build_controllability(nets, inputs, gates_list):
    CC0 = {n: (1 if n in inputs else math.inf) for n in nets}
    CC1 = {n: (1 if n in inputs else math.inf) for n in nets}
    changed = True
    while changed:
        changed = False
        for gtype, out_net, in_nets in gates_list:
            c0 = [CC0[n] for n in in_nets]
            c1 = [CC1[n] for n in in_nets]
            gt = gtype.upper()
            if 'NAND' in gt:
                new0, new1 = 1 + min(c0), 1 + sum(c1)
            elif 'AND' in gt:
                new0, new1 = 1 + sum(c0), 1 + min(c1)
            elif 'NOR' in gt:
                new0, new1 = 1 + sum(c1), 1 + min(c0)
            elif 'OR' in gt:
                new0, new1 = 1 + min(c0), 1 + sum(c1)
            elif 'XNOR' in gt and len(in_nets) == 2:
                a0, b0 = c0; a1, b1 = c1
                new0 = 1 + min(a0 + b0, a1 + b1)
                new1 = 1 + min(a0 + b1, a1 + b0)
            elif 'XOR' in gt and len(in_nets) == 2:
                a0, b0 = c0; a1, b1 = c1
                new0 = 1 + min(a0 + b1, a1 + b0)
                new1 = 1 + min(a0 + b0, a1 + b1)
            else:
                new0, new1 = 1 + c1[0], 1 + c0[0]
            if new0 < CC0[out_net]:
                CC0[out_net] = new0; changed = True
            if new1 < CC1[out_net]:
                CC1[out_net] = new1; changed = True
    control = {f'CC0_{n}': CC0[n] for n in nets}
    control.update({f'CC1_{n}': CC1[n] for n in nets})
    return control

def build_observability(nets, outputs, fanout_list, control, gates_list):
    CO = {n: (1 if n in outputs else math.inf) for n in nets}
    fmap = defaultdict(list)
    for src, dsts in fanout_list:
        for d in dsts:
            fmap[src].append(d)
    changed = True
    while changed:
        changed = False
        for src, dsts in fmap.items():
            mco = min(CO[d] for d in dsts)
            if mco < CO[src]:
                CO[src] = mco; changed = True
        for gtype, out_net, in_nets in gates_list:
            coo = CO[out_net]
            i1 = in_nets[0]
            i2 = in_nets[1] if len(in_nets) > 1 else i1
            c0_i1, c1_i1 = control[f'CC0_{i1}'], control[f'CC1_{i1}']
            c0_i2, c1_i2 = control[f'CC0_{i2}'], control[f'CC1_{i2}']
            gt = gtype.upper()
            if 'AND' in gt or 'NAND' in gt:
                n1 = coo + c1_i2 + 1
                n2 = coo + c1_i1 + 1
            elif 'OR' in gt or 'NOR' in gt:
                n1 = coo + c0_i2 + 1
                n2 = coo + c0_i1 + 1
            elif 'XOR' in gt or 'XNOR' in gt:
                m = min(c0_i2 + c1_i2, c0_i1 + c1_i1)
                n1 = n2 = coo + m + 1
            else:
                n1 = n2 = coo + 1
            if n1 < CO[i1]:
                CO[i1] = n1; changed = True
            if n2 < CO[i2]:
                CO[i2] = n2; changed = True
    return {f'CO_{n}': CO[n] for n in nets}

def write_scoap(control, observ, filename):
    try:
        with open(filename, 'w') as f:
            f.write("--- SCOAP CONTROLLABILITY (CC0) ---\n")
            for k in sorted(control):
                if k.startswith('CC0_'):
                    f.write(f"{k}: {control[k]}\n")
            f.write("\n--- SCOAP CONTROLLABILITY (CC1) ---\n")
            for k in sorted(control):
                if k.startswith('CC1_'):
                    f.write(f"{k}: {control[k]}\n")
            f.write("\n--- SCOAP OBSERVABILITY (CO) ---\n")
            for k in sorted(observ):
                f.write(f"{k}: {observ[k]}\n")
        print(f"SCOAP results written to {filename}")
    except IOError as e:
        print(f"Error writing SCOAP file: {e}", file=sys.stderr)

def main():
    if len(sys.argv) != 2:
        print("Usage: python scoap_calculator.py path/to/out.txt", file=sys.stderr)
        sys.exit(1)
    in_path = sys.argv[1]
    lines = read_netlist(in_path)
    inputs, outputs, fanout_list, gates_list = parse_sections(lines)
    nets = extract_wires(inputs, outputs, fanout_list, gates_list)
    control = build_controllability(nets, inputs, gates_list)
    observ = build_observability(nets, outputs, fanout_list, control, gates_list)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_file = os.path.join(script_dir, 'scoap_out.txt')
    write_scoap(control, observ, out_file)

if __name__ == '__main__':
    main()
