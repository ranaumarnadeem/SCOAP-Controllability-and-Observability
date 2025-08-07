# 🚀 OpenTestability Quick Start Guide

## Super Easy Usage (No more `python3` needed!)

### For WSL Users (Recommended)
```bash
# Just run commands directly!
./opentestability help           # Show all commands
./opentestability workflow       # Show complete workflow  
./opentestability status         # Check project status

# Run analysis in one line each
./opentestability parse design.v output.txt --json
./opentestability scoap output.txt results.txt --json  
./opentestability dag output.json
./opentestability graph output_dag.json
./opentestability reconverge output_dag.json
```

### Quick Commands Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `help` | Show all commands or help for specific command | `./opentestability help parse` |
| `workflow` | Show complete analysis workflow | `./opentestability workflow` |
| `status` | Show file counts and project status | `./opentestability status` |
| `parse` | Convert Verilog → Internal format | `./opentestability parse design.v output.txt` |
| `scoap` | Compute testability metrics | `./opentestability scoap input.txt results.txt` |
| `dag` | Build graph representation | `./opentestability dag input.json` |
| `graph` | Generate visualization | `./opentestability graph dag.json` |
| `reconverge` | Detect fanout structures | `./opentestability reconverge dag.json` |

### 5-Minute Complete Analysis

```bash
# 1. Check what files you have
./opentestability status

# 2. Parse a netlist (creates both .txt and .json)
./opentestability parse priority_encoder.v priority_enc.txt --json

# 3. Run complete analysis
./opentestability scoap priority_enc.txt scoap_results.txt --json
./opentestability dag priority_enc.json  
./opentestability graph priority_enc_dag.json
./opentestability reconverge priority_enc_dag.json

# 4. Check results
./opentestability status
```

### File Organization (Automatic)

```
data/
├── input/           ← Put your .v files here
├── parsed/          ← Converted files appear here  
├── results/         ← SCOAP analysis results
├── dag_output/      ← Graph representations
├── graphs/          ← PNG visualizations
└── reconvergence_output/ ← Fanout analysis
```

### Need Help?

- `./opentestability help` - List all commands
- `./opentestability help <command>` - Detailed help for specific command
- `./opentestability workflow` - See complete workflow with examples
- `./opentestability status` - Check current file counts

