'''
Verilog netlist parser: Detailed per-instance and net listing
Outputs out.txt with lines like:

  AND out(g12) in(g5 g7)
  DFF out(q1) in(d1 clk)
  INPUT g100 g101 g102
  OUTPUT g200
  FANOUT g5 g12 g15

Install: pip install pyverilog
Usage: python verilog_parser.py <netlist.v>
'''
import sys
from collections import defaultdict
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import ModuleDef, InstanceList, Input, Output, Wire

OUTPUT_FILE = 'out.txt'
# Common output port names (nets driven by instances)
OUTPUT_PORT_NAMES = {'Z', 'ZN', 'Q', 'QN', 'Y'}


def parse_verilog_netlist(file_path):
    ast, _ = parse([file_path])
    description = ast.description
    modules = {}

    for module in description.definitions:
        if not isinstance(module, ModuleDef):
            continue
        mod_name = module.name
        # Collect nets
        primary_inputs, primary_outputs, wires = [], [], []
        instances = []

        for item in module.items:
            if isinstance(item, Input):
                primary_inputs.append(item.name)
            elif isinstance(item, Output):
                primary_outputs.append(item.name)
            elif isinstance(item, Wire):
                wires.append(item.name)
            elif isinstance(item, InstanceList):
                for inst in item.instances:
                    conns = {port.portname: getattr(port.argname, 'name', str(port.argname))
                             for port in inst.portlist}
                    instances.append((item.module, inst.name, conns))

        # Build fanout (loads) map
        loads = defaultdict(list)
        for _, name, conns in instances:
            for port, net in conns.items():
                if port not in OUTPUT_PORT_NAMES:
                    loads[net].append(f"{name}")

        modules[mod_name] = {
            'pi': primary_inputs,
            'po': primary_outputs,
            'wires': wires,
            'instances': instances,
            'loads': loads
        }
    return modules


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <verilog_netlist.v>")
        sys.exit(1)

    netlist_file = sys.argv[1]
    data = parse_verilog_netlist(netlist_file)

    with open(OUTPUT_FILE, 'w') as out:
        for mod, info in data.items():
            # Instances: gate/FF list
            for typ, name, conns in info['instances']:
                # find driven nets
                driven = [net for port, net in conns.items() if port in OUTPUT_PORT_NAMES]
                driven_str = ' '.join(driven) if driven else 'NONE'
                # find input nets
                inputs = [net for port, net in conns.items() if port not in OUTPUT_PORT_NAMES]
                in_str = ' '.join(inputs) if inputs else 'NONE'
                out.write(f"{typ} out({driven_str}) in({in_str})\n")

            # Primary inputs and outputs
            if info['pi']:
                out.write("INPUT " + ' '.join(info['pi']) + "\n")
            if info['po']:
                out.write("OUTPUT " + ' '.join(info['po']) + "\n")

            # Fanout per net
            for net, dests in info['loads'].items():
                if dests:
                    out.write(f"FANOUT {net} " + ' '.join(dests) + "\n")
    print(f"Parsing complete. Written output to {OUTPUT_FILE}")
