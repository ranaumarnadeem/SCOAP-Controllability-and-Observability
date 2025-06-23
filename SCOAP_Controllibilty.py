# SCOAP Controllability and Observability Calculation Script

def read_netlist(filename):
    with open(filename) as f:
        lines = f.readlines()
    return [line.strip().split() for line in lines]

def parse_netlist(m):
    fanout_list, out_in_fanout_list, gates_list, input_list = [], [], [], []
    for line in m:
        if line[0] in ['INPUT', 'OUTPUT', 'FANOUT']:
            out_in_fanout_list.append(line)
            if line[0] == 'INPUT':
                input_list.extend(map(int, line[1:]))
            if line[0] == 'FANOUT':
                fanout_list.append(line)
        else:
            gates_list.append(line)
    return fanout_list, out_in_fanout_list, gates_list, input_list

def extract_wires(m):
    wires = set()
    for line in m:
        wires.update(map(int, line[1:]))
    return sorted(wires)

def build_controllability(wires_list, input_list, fanout_list):
    control = {f'CC0_{w}': 0 for w in wires_list}
    control.update({f'CC1_{w}': 0 for w in wires_list})
    
    for w in input_list:
        control[f'CC0_{w}'] = 1
        control[f'CC1_{w}'] = 1

    fanin_map = {int(f[2]): int(f[1]) for f in fanout_list for i in f[2:]}
    
    for key in control:
        wire = int(key.split('_')[1])
        if wire in fanin_map:
            control[key] = control[key.split('_')[0] + '_' + str(fanin_map[wire])]

    return control

def build_observability(wires_list, out_in_fanout_list, fanout_list, control, gates_list):
    Observe = {f'CO_{w}': 0 for w in wires_list}
    
    outputs = []
    for line in out_in_fanout_list:
        if line[0] == 'OUTPUT':
            outputs.extend(map(int, line[1:]))
    for w in outputs:
        Observe[f'CO_{w}'] = 1

    fanout_map = {int(f[1]): list(map(int, f[2:])) for f in fanout_list}

    for wire, fanouts in fanout_map.items():
        min_co = min([Observe[f'CO_{f}'] for f in fanouts])
        Observe[f'CO_{wire}'] = min_co

    def find_gate_by_output(w):
        for g in gates_list:
            if int(g[1]) == w:
                return g[0], list(map(int, g[2:]))
        return None, []

    for g in gates_list:
        out = int(g[1])
        in1, in2 = map(int, g[2:4])
        co_out = Observe[f'CO_{out}']
        gate = g[0]

        if gate in ['AND', 'NAND']:
            co_in1 = co_out + control[f'CC1_{in2}'] + 1
            co_in2 = co_out + control[f'CC1_{in1}'] + 1
        elif gate in ['OR', 'NOR']:
            co_in1 = co_out + control[f'CC0_{in2}'] + 1
            co_in2 = co_out + control[f'CC0_{in1}'] + 1
        elif gate in ['XOR', 'XNOR']:
            min_val = min(control[f'CC0_{in2}'] + control[f'CC1_{in2}'],
                          control[f'CC0_{in1}'] + control[f'CC1_{in1}'])
            co_in1 = co_in2 = co_out + min_val + 1
        else:
            co_in1 = co_in2 = co_out + 1

        Observe[f'CO_{in1}'] = co_in1
        Observe[f'CO_{in2}'] = co_in2

    return Observe

def print_scoap(control, Observe):
    print("\n--- SCOAP CONTROLLABILITY ---")
    for key in sorted(control.keys(), key=lambda x: (int(x.split('_')[1]), x)):
        print(f"{key}: {control[key]}")

    print("\n--- SCOAP OBSERVABILITY ---")
    for key in sorted(Observe.keys(), key=lambda x: int(x.split('_')[1])):
        print(f"{key}: {Observe[key]}")

# === Main ===
filename = 'mux.txt'
m = read_netlist(filename)
fanout_list, out_in_fanout_list, gates_list, input_list = parse_netlist(m)
wires_list = extract_wires(m)
control = build_controllability(wires_list, input_list, fanout_list)
Observe = build_observability(wires_list, out_in_fanout_list, fanout_list, control, gates_list)
print_scoap(control, Observe)
