from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import InstanceList, Instance, Input, Output, Wire

def parse_verilog_netlist(file_path):
    ast, _ = parse([file_path])
    description = ast.description

    modules = {}
    for module in description.definitions:
        mod_name = module.name
        inputs, outputs, wires, gates, flipflops = [], [], [], [], []

        for item in module.items:
            if isinstance(item, Input):
                inputs.append(item.name)
            elif isinstance(item, Output):
                outputs.append(item.name)
            elif isinstance(item, Wire):
                wires.append(item.name)
            elif isinstance(item, InstanceList):
                for inst in item.instances:
                    gate_type = item.module
                    conns = {p.portname: p.argname.name for p in inst.portlist}
                    # Heuristic: if it contains D/Q/CK → it's a flip-flop
                    if any(x in conns for x in ['D', 'Q', 'CK']):
                        flipflops.append((gate_type, inst.name, conns))
                    else:
                        gates.append((gate_type, inst.name, conns))

        modules[mod_name] = {
            "inputs": inputs,
            "outputs": outputs,
            "wires": wires,
            "gates": gates,
            "flipflops": flipflops
        }

    return modules
if __name__ == "__main__":
    netlist_info = parse_verilog_netlist("s15850_netlist_dft.v")
    for mod, data in netlist_info.items():
        print(f"\nModule: {mod}")
        print("Inputs:", data['inputs'])
        print("Outputs:", data['outputs'])
        print("Wires:", len(data['wires']))
        print("Total Gates:", len(data['gates']))
        print("Total Flip-Flops:", len(data['flipflops']))
