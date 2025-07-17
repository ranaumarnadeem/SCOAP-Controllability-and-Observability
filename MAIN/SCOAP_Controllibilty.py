#!/usr/bin/env python3
# scoap_calculator.py

import sys
import os
import re
import math
import json
from collections import defaultdict

def expand_vector(signal):
    m = re.match(r'^(\w+)\[(\d+):(\d+)\]$', signal)
    if not m:
        return [signal]
    base, msb, lsb = m.group(1), int(m.group(2)), int(m.group(3))
    if msb >= lsb:
        # go from msb down to lsb *inclusive*
        return [f"{base}[{i}]" for i in range(msb, lsb - 1, -1)]
    else:
        # go from msb up to lsb *inclusive*
        return [f"{base}[{i}]" for i in range(msb, lsb + 1)]

def read_netlist(filename):
    try:
        with open(filename) as f:
            return [line.rstrip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: cannot open '{filename}'", file=sys.stderr)
        sys.exit(1)

def parse_sections(lines):
    inputs, outputs = [], []
    fanout_list, gates_list = [], []
    section = None
    gate_re = re.compile(r'^\s*(\w+)\s+out\(\s*([^)]+)\)\s+in\(\s*([^)]+)\)\s*$')
    for lineno, line in enumerate(lines, start=1):
        if line.startswith('#'):
            if 'Primary Inputs' in line:    section = 'INPUT'
            elif 'Primary Outputs' in line: section = 'OUTPUT'
            elif 'FAN OUT' in line:         section = 'FANOUT'
            elif 'Complete Paths' in line:  section = 'GATES'
            else:                           section = None
            continue
        if section == 'GATES' and any(line.startswith(p) for p in ('INPUT ','OUTPUT ','FANOUT ')):
            continue
        if section == 'INPUT':
            for tok in line.split():
                inputs.extend(expand_vector(tok))
        elif section == 'OUTPUT':
            for tok in line.split():
                outputs.extend(expand_vector(tok))
        elif section == 'FANOUT':
            # fanout_list parsing commented out
            continue
        elif section == 'GATES':
            m = gate_re.match(line)
            if not m:
                print(f"[WARN] skipped @{lineno}: {line}", file=sys.stderr)
            else:
                gtype = m.group(1)
                outs  = m.group(2).split()
                ins   = m.group(3).split()
                for o in outs:
                    gates_list.append((gtype, o, ins))
    print(f"=== DEBUG: Inputs={inputs}, Outputs={outputs}, Gates={len(gates_list)} ===")
    return inputs, outputs, fanout_list, gates_list

def extract_wires(inputs, outputs, fanout_list, gates_list):
    nets = set(inputs)|set(outputs)
    for _, o, ins in gates_list:
        nets.add(o); nets.update(ins)
    return sorted(nets)

def build_controllability(nets, inputs, gates_list):
    CC0 = {n:(1 if n in inputs else math.inf) for n in nets}
    CC1 = {n:(1 if n in inputs else math.inf) for n in nets}
    changed = True
    while changed:
        changed = False
        for gtype,o,ins in gates_list:
            c0=[CC0[n] for n in ins]; c1=[CC1[n] for n in ins]; gt=gtype.upper()
            try:
                if 'NAND' in gt:              new0,new1=1+min(c0),1+sum(c1)
                elif 'AND' in gt:             new0,new1=1+sum(c0),1+min(c1)
                elif 'NOR' in gt:             new0,new1=1+sum(c1),1+min(c0)
                elif 'OR' in gt:              new0,new1=1+min(c0),1+sum(c1)
                elif 'XNOR' in gt and len(ins)==2:
                                              a0,b0=c0; a1,b1=c1
                                              new0=1+min(a0+b0,a1+b1)
                                              new1=1+min(a0+b1,a1+b0)
                elif 'XOR' in gt and len(ins)==2:
                                              a0,b0=c0; a1,b1=c1
                                              new0=1+min(a0+b1,a1+b0)
                                              new1=1+min(a0+b0,a1+b1)
                elif 'INV' in gt or 'NOT' in gt: new0, new1 = 1+c1[0], 1+c0[0]
                elif 'BUF' in gt:               new0, new1 = 1+c0[0], 1+c1[0]
                else:                           new0, new1 = 1+c1[0], 1+c0[0]
            except IndexError:
                continue
            if new0<CC0[o]: CC0[o],changed=new0,True
            if new1<CC1[o]: CC1[o],changed=new1,True
    ctrl={f"CC0_{n}":CC0[n] for n in nets}
    ctrl.update({f"CC1_{n}":CC1[n] for n in nets})
    return ctrl

def build_observability(nets, outputs, fanout_list, control, gates_list):
    CO={n:(1 if n in outputs else math.inf) for n in nets}
    changed=True
    while changed:
        changed=False
        for gtype,o,ins in gates_list:
            coo=CO[o]; gt=gtype.upper()
            try:
                if len(ins)==1:
                    v=coo+1
                    if v<CO[ins[0]]: CO[ins[0]],changed=v,True
                    continue
                i1,i2=ins[0],ins[1]
                c0_i1, c1_i1 = control[f"CC0_{i1}"], control[f"CC1_{i1}"]
                c0_i2, c1_i2 = control[f"CC0_{i2}"], control[f"CC1_{i2}"]
                if 'AND' in gt or 'NAND' in gt:
                    n1,n2 = coo+c1_i2+1, coo+c1_i1+1
                elif 'OR' in gt  or 'NOR' in gt:
                    n1,n2 = coo+c0_i2+1, coo+c0_i1+1
                elif 'XOR' in gt or 'XNOR' in gt:
                    m=min(c0_i2+c1_i2, c0_i1+c1_i1)
                    n1=n2=coo+m+1
                else:
                    n1=n2=coo+1
                if n1<CO[i1]: CO[i1],changed=n1,True
                if n2<CO[i2]: CO[i2],changed=n2,True
            except:
                continue
    return {f"CO_{n}":CO[n] for n in nets}

def write_scoap(control, observ, filename):
    with open(filename,'w') as f:
        f.write("--- SCOAP CONTROLLABILITY (CC0) ---\n")
        for k in sorted(control):
            if k.startswith("CC0_"): f.write(f"{k}: {control[k]}\n")
        f.write("\n--- SCOAP CONTROLLABILITY (CC1) ---\n")
        for k in sorted(control):
            if k.startswith("CC1_"): f.write(f"{k}: {control[k]}\n")
        f.write("\n--- SCOAP OBSERVABILITY (CO) ---\n")
        for k in sorted(observ):
            f.write(f"{k}: {observ[k]}\n")
    print(f"SCOAP results written to {filename}")

def dump_json(control, observ, inputs, outputs, gates_list, output_path):
    from math import isinf
    data = {"primary_inputs":inputs, "primary_outputs":outputs, "gates":[]}

    # actual gates
    for idx,(gtype,o,ins) in enumerate(gates_list):
        name = o if o.startswith("UNCONNECTED") else f"{gtype}_{idx}"
        gi = {
            "name": name,
            "type": gtype,
            "inputs": ins,
            "output": o,
            "cc0": control.get(f"CC0_{o}"),
            "cc1": control.get(f"CC1_{o}"),
            "co":  observ.get(f"CO_{o}", math.inf)
        }
        for k in ("cc0","cc1","co"):
            v=gi[k]
            gi[k] = "NA" if v is None else ("Infinity" if isinstance(v,float) and isinf(v) else v)
        data["gates"].append(gi)

    # standalone PIs/POs
    for net in sorted(set(inputs+outputs)):
        gi = {
            "name": net, "type":"NET", "inputs":[], "output":net,
            "cc0": control.get(f"CC0_{net}"),
            "cc1": control.get(f"CC1_{net}"),
            "co":  observ.get(f"CO_{net}", math.inf)
        }
        for k in ("cc0","cc1","co"):
            v=gi[k]
            gi[k] = "NA" if v is None else ("Infinity" if isinstance(v,float) and isinf(v) else v)
        data["gates"].append(gi)

    with open(output_path,'w') as f:
        json.dump(data,f,indent=4)
    print(f"[✓] JSON SCOAP written to {output_path}")

def reconstruct_fanouts(gates_list):
    fmap=defaultdict(list)
    for _,o,ins in gates_list:
        for i in ins: fmap[i].append(o)
    return list(fmap.items())

def main():
    if len(sys.argv)<2 or len(sys.argv)>3:
        print("Usage: python scoap_calculator.py out.txt [--json]",file=sys.stderr)
        sys.exit(1)
    path=sys.argv[1]
    want_json = "--json" in sys.argv

    lines=read_netlist(path)
    inputs,outputs,fanout_list,gates_list = parse_sections(lines)
    # fanout_list is unused/commented
    if not fanout_list:
        fanout_list = reconstruct_fanouts(gates_list)

    nets = extract_wires(inputs,outputs,fanout_list,gates_list)
    ctrl = build_controllability(nets,inputs,gates_list)
    obs  = build_observability(nets,outputs,fanout_list,ctrl,gates_list)

    base=os.path.dirname(os.path.abspath(__file__))
    write_scoap(ctrl,obs, os.path.join(base,"scoap_out.txt"))
    if want_json:
        dump_json(ctrl,obs,inputs,outputs,gates_list,os.path.join(base,"scoap_out.json"))

if __name__=="__main__":
    main()
