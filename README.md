# OpenTestability

**Comprehensive Gate-Level Testability Metric Analyzer**

OpenTestability is an open-source Python framework for analyzing testability in gate-level digital designs. It currently supports **SCOAP (Sandia Controllability/Observability Analysis Program)** for combinational circuits and is actively being extended to include:

- Reconvergent Fanout Detection  
- Cycle Observability Probability (COP)  
- Path Distance Metrics  
- Sequential Testability Analysis

Originally a personal project, OpenTestability is now a growing tool aimed at researchers, students, and DFT engineers who want to understand or evaluate the testability of synthesized netlists easily without expensive licensing.

[![License](https://img.shields.io/github/license/ranaumarnadeem/OpenTestability)](https://github.com/ranaumarnadeem/OpenTestability/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Issues](https://img.shields.io/github/issues/ranaumarnadeem/OpenTestability)](https://github.com/ranaumarnadeem/OpenTestability/issues)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen)](https://github.com/ranaumarnadeem/OpenTestability/blob/main/CONTRIBUTING.md)



## Features

OpenTestability is an open source Python-based toolkit designed to analyze and improve the testability of gate-level netlists. It currently supports:

### Implemented

- Combinational SCOAP Metrics: Calculates CC0 (Controllability to 0), CC1 (Controllability to 1), and CO (Observability)
- Netlist Parser: Converts Synopsys DC / Cadence Genus outputs into a clean intermediate format
- Graph Representation: Uses NetworkX to build a Directed Acyclic Graph (DAG) from the netlist

### In Development

- Reconvergent Fanout Detection: Identifies complex reconvergent paths which hinder test coverage
- Cycle Observability Probability (COP): Statistical estimation of signal visibility at output ports
- Distance Metrics: Compute logic depth from inputs to outputs or between FFs
- Sequential Testability Metrics: SCOAP extensions for sequential circuits using latch/FF awareness
- Visualization: Fanout cones and DAGs using Graphviz

### Designed for Researchers and Students

OpenTestability is modular and readable, aiming to serve as a learning platform as well as a research-grade tool.

## Use Cases

- Evaluate the testability of ASIC or SoC blocks post-synthesis.
- Identify weakly observable or hard-to-control nodes for DFT improvement.
- Assist in placement of scan chain elements by highlighting low-SCOAP areas.
- Analyze reconverging fanouts for ATPG and fault coverage enhancement.
- Use as a teaching/research tool in VLSI and DFT coursework.

## 📦 Installation

Before running OpenTestability, make sure you have the following installed:

- Python 3.8+
- pip (Python package manager)
- (Optional) Graphviz for visualization support

### 1. Clone the Repository

```bash
git clone https://github.com/ranaumarnadeem/OpenTestability.git
cd OpenTestability
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. (Optional) Install Graphviz

#### On Ubuntu/Debian:
```bash
sudo apt-get install graphviz
```

#### On macOS:
```bash
brew install graphviz
```

#### On Windows:
Download from https://graphviz.org/download/

## 🚀 Quick Start

### 1. Usage



```bash
# Get help and see all commands
./opentestability help

# Show complete workflow  
./opentestability workflow

# Check your project status
./opentestability status
```

### 2. Run Complete Analysis 

```bash
# 1. Parse a Verilog netlist  
./opentestability parse priority_encoder.v priority_enc.txt --json

# 2. Compute SCOAP metrics
./opentestability scoap priority_enc.txt scoap_results.txt --json

# 3. Build DAG representation
./opentestability dag priority_enc.json

# 4. Generate visualization  
./opentestability graph priority_enc_dag.json

# 5. Detect reconvergent fanout
./opentestability reconverge priority_enc_dag.json
```

**📖 See [QUICKSTART.md](QUICKSTART.md) for the 5-minute tutorial!**

Results are automatically organized in the `data/` directory structure.

## 📁 Project Structure

```
OpenTestability/
├── src/                           # Source code
│   └── opentestability/          # Main package
│       ├── __init__.py
│       ├── core/                 # Core algorithms
│       │   ├── __init__.py
│       │   ├── scoap.py         # SCOAP testability metrics
│       │   ├── dag_builder.py   # DAG construction
│       │   └── reconvergence.py # Reconvergent fanout detection
│       ├── parsers/             # Input/output parsers
│       │   ├── __init__.py
│       │   ├── verilog_parser.py # Verilog netlist parser
│       │   └── json_converter.py # JSON format converter
│       ├── visualization/       # Graph visualization
│       │   ├── __init__.py
│       │   └── graph_renderer.py # Graphviz-based rendering
│       └── utils/               # Utilities
│           ├── __init__.py
│           └── file_utils.py    # File and path management
├── data/                        # Input/output data
│   ├── input/                   # Input netlists
│   ├── parsed/                  # Parsed netlists
│   ├── results/                 # Analysis results
│   ├── graphs/                  # Generated visualizations
│   ├── dag_output/              # DAG JSON files
│   └── reconvergence_output/    # Reconvergence analysis
├── examples/                    # Example designs and scripts
│   ├── designs/                 # Sample netlists
│   └── scripts/                 # Synthesis scripts
├── tests/                       # Test suite
├── main.py                      # CLI entry point
├── setup.py                     # Package installation
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
├── CONTRIBUTING.md              # Contribution guidelines
└── LICENSE                      # Open-source license
```

## 🚀 Usage


### Get Help Anytime

```bash
./opentestability help              # Show all commands
./opentestability help <command>    # Detailed help for specific command  
./opentestability workflow          # Show complete workflow
./opentestability status            # Check project status
```

### Parse a Netlist

```bash
./opentestability parse raw_netlist.v parsed_design.txt --json
```

Parsed files saved to `data/parsed/`.

### Run SCOAP Analysis

```bash
./opentestability scoap parsed_design.txt scoap_results.txt --json
```

Results saved to `data/results/`.

### Build DAG Representation

```bash
./opentestability dag parsed_design.json
```

DAG files saved to `data/dag_output/`.

### Generate Visualization

```bash
./opentestability graph design_dag.json
```

Graphs saved to `data/graphs/`.

### Detect Reconvergent Fanout

```bash
./opentestability reconverge design_dag.json
```

Analysis results saved to `data/reconvergence_output/`.

### WSL Users (Virtual Environment)

The CLI automatically works with your WSL virtual environment - just run the commands directly!

### Argument Summary
### Argument Summary

| Flag             | Description                                        | Example                                          |
|------------------|----------------------------------------------------|--------------------------------------------------|
| `--parse`        | Parse a raw gate-level netlist                     | `--parse -i raw_netlist.v -o out.txt`            |
| `--scoap`        | Run SCOAP analysis on parsed netlist               | `--scoap -i <input.v> -o scoap_result.json|txt`  |
| `-i, --input`    | Specify input file path                            | `-i netlist/my_design.v`                         |
| `-o, --output`   | Specify output file name                           | `-o analysis_results.json`                       |
| `--format`       | Output format (json or txt)                        | `--format json`                                  |
| `--verbose`      | Enable detailed logging                            | `--verbose`                                      |
| `--help`         | Show help message and exit                         | `--help`                                         |

## 🤝 Contributing

We welcome all kinds of contributions—from fixing bugs and writing tests to suggesting new features.

### How to Contribute

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/your-username/OpenTestability.git
   cd OpenTestability
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a new branch:
   ```bash
   git checkout -b my-feature
   ```

4. Make your changes, add tests, and commit:
   ```bash
   git commit -m "Add: My awesome feature"
   ```

5. Push and open a pull request:
   ```bash
   git push origin my-feature
   ```

### Code Guidelines

- Follow [PEP8](https://peps.python.org/pep-0008/)
- Add docstrings and keep logic modular
- Keep CLI consistent and testable

### Running Tests

```bash
pytest tests/
```

### We're Especially Looking For:

- Sequential SCOAP support
- COP and distance metric algorithms
- Reconvergence graph improvements
- DAG/metric visualizations
- Fault simulation logic

## 📄 License

This project is licensed under the **MIT License**.

You are free to:

- ✅ Use it for commercial or personal purposes  
- 🛠 Modify and distribute the source code  
- 🔗 Include it in proprietary software (with attribution)

See the [LICENSE](./LICENSE) file for full terms.

---

Whether you're using this for class, research, or chip tapeout—thank you for checking out OpenTestability!
