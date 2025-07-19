import os
from collections import defaultdict
from pyverilog.vparser.parser import parse as v_parse
from pyverilog.vparser.ast import ModuleDef, InstanceList, Decl, Input, Output, Wire

OUTPUT_PORT_NAMES = {'Z', 'ZN', 'Q', 'QN', 'Y', 'S', 'CO'}
CURRENT_DIR     = os.path.dirname(os.path.abspath(__file__))
NETLIST_DIR     = os.path.join(CURRENT_DIR, 'netlist')
PARSED_DIR      = os.path.join(CURRENT_DIR, 'parsednetlist')

def get_argname_name(arg):
    if hasattr(arg, 'name'):
        return arg.name
    if hasattr(arg, 'var') and hasattr(arg.var, 'name') and hasattr(arg, 'ptr'):
        return f"{arg.var.name}[{arg.ptr.value}]"
    return str(arg)

def format_port(port):
    if getattr(port, 'width', None):
        msb = port.width.msb.value
        lsb = port.width.lsb.value
        return f"{port.name}[{msb}:{lsb}]"
    return port.name

def parse_verilog_netlist(file_path):
    ast, _ = v_parse([file_path])
    modules = {}
    for module in ast.description.definitions:
        if not isinstance(module, ModuleDef):
            continue
        pi, po, wires, instances = [], [], [], []
        for item in module.items:
            if isinstance(item, Decl):
                for decl in item.list:
                    if isinstance(decl, Input):  pi.append(format_port(decl))
                    if isinstance(decl, Output): po.append(format_port(decl))
                    if isinstance(decl, Wire):   wires.append(decl.name)
            elif isinstance(item, InstanceList):
                for inst in item.instances:
                    conns = {p.portname: get_argname_name(p.argname) for p in inst.portlist}
                    instances.append((item.module, inst.name, conns))
        modules[module.name] = {
            'pi': pi, 'po': po, 'wires': wires,
            'instances': instances
        }
    return modules

def parse(input_filename: str, output_filename: str) -> str:
    """
    Parses netlist/<input_filename> and writes to parsednetlist/<output_filename>.
    Returns the full path of the file written.
    """
    input_path  = os.path.join(NETLIST_DIR, input_filename)
    output_path = os.path.join(PARSED_DIR, output_filename)

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Could not find input netlist: {input_path}")

    os.makedirs(PARSED_DIR, exist_ok=True)
    data = parse_verilog_netlist(input_path)

    with open(output_path, 'w') as out:
        for mod, info in data.items():
            out.write('# Primary Inputs\n')
            out.write(' '.join(info['pi']) + '\n\n')

            out.write('# Primary Outputs\n')
            out.write(' '.join(info['po']) + '\n\n')

            out.write('# Complete Paths\n')
            cnt = 0
            for typ, inst_name, conns in info['instances']:
                outputs = [(p, n) for p, n in conns.items() if p in OUTPUT_PORT_NAMES]
                inputs  = [ n for p, n in conns.items() if p not in OUTPUT_PORT_NAMES]
                if not outputs:
                    out.write(f"{typ} out(UNCONNECTED{cnt}) in({' '.join(inputs)})\n")
                    cnt += 1
                else:
                    for p, n in outputs:
                        out.write(f"{typ} out({n}) in({' '.join(inputs)})\n")
                        cnt += 1

            if info['pi']:
                out.write('\nINPUT '  + ' '.join(info['pi']) + '\n')
            if info['po']:
                out.write('OUTPUT ' + ' '.join(info['po']) + '\n')

    return output_path
