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

### 1. Prepare Your Netlist

Ensure your gate-level netlist is exported from tools like Genus or Synopsys DC. You may need to run the parser to convert it into the accepted format. Some samples are already available in the `data/` directory.

### 2. Run SCOAP Metric Generator

```bash
python3 main.py --scoap parsednetlist/my_parsed.txt -o scoap_result.json
```

This saves results in `scoapout/`.

### 3. Run Netlist Parser

```bash
python3 main.py --parse raw_netlist.txt
```

This saves the parsed netlist in `parsednetlist/`.

## 📁 Project Structure

```
OpenTestability/
├── code/
│   ├── __init__.py
│   ├── parser.py           # Parses raw gate-level netlists into internal format
│   ├── scoap.py            # Computes combinational SCOAP metrics
│   ├── reconvergence.py    # Reconvergent fanout detection logic
│   ├── dag_builder.py      # Builds DAG using NetworkX from parsed netlist
│   └── utils.py            # Utility functions for file I/O, name cleaning, etc.
├── parsednetlist/          # Output directory for parsed netlists
├── scoapout/               # Output directory for SCOAP metric results
├── data/
│   └── sample_netlist.txt  # Example input gate-level netlist
├── examples/
│   └── demo_scoap_run.py   # Example usage script
├── tests/
│   ├── test_parser.py      # Unit tests for the parser module
│   ├── test_scoap.py       # Unit tests for SCOAP calculations
│   └── test_dag.py         # Unit tests for DAG builder
├── main.py                 # Main CLI entry point
├── requirements.txt        # Python dependencies
├── README.md               # Project overview and usage guide
├── CONTRIBUTING.md         # Contribution guidelines
└── LICENSE                 # Open-source license
```

## 🚀 Usage

The main entry point is `main.py`.

### Parse a Netlist

```bash
python3 main.py --parse raw_netlist.txt
```

Parsed file will be saved to `parsednetlist/`.

### Run SCOAP Analysis

```bash
python3 main.py --scoap parsednetlist/my_parsed.txt -o scoap_result.json
```

JSON results are saved to `scoapout/`.

### Argument Summary

| Flag             | Description                                        | Example                             |
|------------------|----------------------------------------------------|-------------------------------------|
| `--parse`        | Parse a raw gate-level netlist                     | `--parse raw_netlist.txt`           |
| `--scoap`        | Run SCOAP analysis on parsed netlist               | `--scoap parsednetlist/file.txt`    |
| `-o`             | Output file name for SCOAP metrics (JSON)          | `-o scoap_result.json`              |

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
