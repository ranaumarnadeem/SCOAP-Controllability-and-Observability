# 🔍 Verilog Netlist Parser for DFT Automation

This project provides a **robust parser for Verilog netlists** aimed at **Design-for-Testability (DFT)** research and automation. It is specifically built to handle **gate-level netlists** (output of tools like Synopsys Genus, IC Compiler, etc.) and extract the following:

- **Logic gates** with output/input nets
- **Flip-flops**
- **Primary Inputs and Outputs**
- **Internal wires**
- **Fan-in and Fan-out nets**

> 📌 **Note**: This project is still under active development. The next milestone is integrating a **Controllability and Observability (COP/SCOAP)** calculator by adapting the work of [Dr. Rathnamala Rao](https://github.com/rathnamala-rao), whose SCOAP calculator has been forked for this purpose.

---

## 🧠 Motivation

Gate-level netlists from tools like Genus or IC Compiler use a Verilog format that is **not directly compatible with most DFT tools or academic SCOAP calculators**.

- Netlist structure varies widely depending on the tool.
- Existing COP/SCOAP tools require manually reformatted inputs.
  
This parser **bridges the gap** between standard tool output and academic DFT metric calculators.

---

## 📦 Features

### ✅ Verilog Netlist Parsing
- Supports standard gate-level Verilog.
- Parses all modules, instances, wires, and ports.

### ✅ DFT-Friendly Summary Output
The parsed summary (`out.txt`) includes:

- `# Primary Inputs`: All PI nets (e.g., `g1`, `CK`, etc.)
- `# Primary Outputs`: All PO nets
- `# FAN IN`: Nets that are used as inputs to multiple components
- `# FAN OUT`: Nets that drive multiple destinations
- `# Complete Paths`: Detailed gate-wise listing:

- `# Complete Paths`: Detailed gate-wise listing:
NAND out(g1243) in(g1244 g1245)
DFF out(q1) in(d1 clk)
...


---

## 📂 File Output Format

The `out.txt` file is structured into labeled sections for easy parsing and analysis:

```verilog
# Primary Inputs
g1 g2 g3 ...

# Primary Outputs
g100 g101 ...

# FAN IN
g45
g46


# FAN OUT
FANOUT g50 g60 g61 g62

# Complete Paths
NAND out(g1243) in(g1244 g1245)
DFF out(q1) in(d1 clk)
```
---

## 🛠️ Technologies

- **Python 3**
- [Pyverilog](https://github.com/PyHDI/Pyverilog) – Verilog parser
- Regex and AST traversal
---

## 🚧 Next Milestone: SCOAP Integration

The parser is being extended to feed data directly into a **SCOAP calculator** for:
- **Controllability (CC0/CC1)**
- **Observability (CO)**

The calculator originally developed by Dr. Rathnamala Rao has been forked. This version will be modified to:
- Accept `out.txt` or in-memory netlist graph from this parser.
- Provide a direct and accurate SCOAP metric dump.

---


## 🤝 Contributing

Contributions are welcome! You can:
- Add support for more Verilog constructs (e.g., more FF types, buffers).
- Optimize fanin/fanout analysis using graph traversal.
- Add JSON output mode for integration with other DFT tools.
- Help convert the `out.txt` format into a SCOAP input graph.

To contribute:
1. Fork this repo
2. Create a new branch (`feature-x`)
3. Commit your changes
4. Open a PR 🎉

---

## 🧪 Example

Given the following Verilog gate-level instance:

```verilog
NAND2X1 U1 ( .A(g3), .B(g4), .Y(g5) );
NAND out(g5) in(g3 g4)
```

In case of Flip-Flop

```verilog
DFFPOSX1 D1 ( .D(g1), .CLK(clk), .Q(g2) );
DFF out(g2) in(g1 clk)
```

---
## 📫 Contact
For questions, feel free to raise an Issue or contact the maintainer.

