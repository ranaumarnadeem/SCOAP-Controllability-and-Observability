'''
Verilog netlist parser: Structured output with sections and complete paths
Install: pip install pyverilog
Usage: python verilog_parser.py <netlist.v>
Produces out.txt with sections:

# Primary Inputs
<list of nets>

# Primary Outputs
<list of nets>

# FAN IN
<nets with drivers>

# FAN OUT
<nets with loads>

# Complete Paths
Detailed instance and net listings:
  <GATE_TYPE> out(<driver>) in(<nets>)
  INPUT <pi1> <pi2> …
  OUTPUT <po1> <po2> …
  FANOUT <net> <load1> <load2> …
'''
import sys
from collections import defaultdict
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import ModuleDef, InstanceList, Decl, Input, Output, Wire

OUTPUT_FILE = 'out.txt'
# Ports considered outputs from instances
OUTPUT_PORT_NAMES = {'Z', 'ZN', 'Q', 'QN', 'Y'}

def parse_verilog_netlist(file_path):
    ast, _ = parse([file_path])
    modules = {}
    for module in ast.description.definitions:
        if not isinstance(module, ModuleDef):
            continue
        pi, po, wires = [], [], []
        instances = []
        # Gather nets and instances
        for item in module.items:
            if isinstance(item, Decl):
                for decl in item.list:
                    if isinstance(decl, Input): pi.append(decl.name)
                    elif isinstance(decl, Output): po.append(decl.name)
                    elif isinstance(decl, Wire): wires.append(decl.name)
            elif isinstance(item, InstanceList):
                for inst in item.instances:
                    conns = {p.portname: getattr(p.argname, 'name', str(p.argname))
                             for p in inst.portlist}
                    instances.append((item.module, inst.name, conns))
        # Build driver/load maps
        drivers = defaultdict(list)
        loads = defaultdict(list)
        for typ, inst_name, conns in instances:
            for port, net in conns.items():
                if port in OUTPUT_PORT_NAMES:
                    drivers[net].append(f"{inst_name}({typ})")
                else:
                    loads[net].append(f"{inst_name}({typ})")
        modules[module.name] = {
            'pi': pi,
            'po': po,
            'wires': wires,
            'drivers': drivers,
            'loads': loads,
            'instances': instances
        }
    return modules

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <verilog_netlist.v>")
        sys.exit(1)
    data = parse_verilog_netlist(sys.argv[1])
    with open(OUTPUT_FILE, 'w') as out:
        for mod, info in data.items():
            all_nets = set(info['pi'] + info['po'] + info['wires'])
            # Primary Inputs
            out.write('# Primary Inputs\n')
            out.write(' '.join(info['pi']) + '\n\n')
            # Primary Outputs
            out.write('# Primary Outputs\n')
            out.write(' '.join(info['po']) + '\n\n')
            # FAN IN
            out.write('# FAN IN\n')
            for net in sorted(all_nets):
                if info['drivers'].get(net):
                    out.write(net + '\n')
            out.write('\n')
            # FAN OUT
            out.write('# FAN OUT\n')
            for net in sorted(all_nets):
                if info['loads'].get(net):
                    out.write(net + '\n')
            out.write('\n')
            # Complete Paths
            out.write('# Complete Paths\n')
            # Instances
            for typ, inst_name, conns in info['instances']:
                driven = [net for port, net in conns.items() if port in OUTPUT_PORT_NAMES]
                inputs = [net for port, net in conns.items() if port not in OUTPUT_PORT_NAMES]
                out.write(f"{typ} out({' '.join(driven)}) in({' '.join(inputs)})\n")
            # PI/PO lines
            if info['pi']:
                out.write('INPUT ' + ' '.join(info['pi']) + '\n')
            if info['po']:
                out.write('OUTPUT ' + ' '.join(info['po']) + '\n')
            # FANOUT detailed
            for net in sorted(all_nets):
                if info['loads'].get(net):
                    out.write(f"FANOUT {net} {' '.join(info['loads'][net])}\n")
    print(f"Parsing complete. Written output to {OUTPUT_FILE}")