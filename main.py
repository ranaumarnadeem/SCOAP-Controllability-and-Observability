#!/usr/bin/env python3
"""
OpenTestability CLI - Main command-line interface.

A comprehensive framework for gate-level testability analysis including
SCOAP metrics, reconvergent fanout detection, and visualization.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src directory to Python path for imports
SCRIPT_DIR = Path(__file__).parent
SRC_DIR = SCRIPT_DIR / 'src'
sys.path.insert(0, str(SRC_DIR))

from opentestability.parsers.verilog_parser import parse as run_parse
from opentestability.parsers.json_converter import convert_txt_to_json
from opentestability.core.scoap import run as run_scoap
from opentestability.core.dag_builder import create_dag_from_netlist
from opentestability.core.reconvergence import analyze_reconvergence
from opentestability.visualization.graph_renderer import visualize_gate_graph
from opentestability.utils.file_utils import get_project_paths


def check_file(path):
    """Check if a file exists and report status."""
    if not Path(path).exists():
        print(f"[✗] Input file not found: {path}")
        sys.exit(1)
    print(f"[✓] Found input file: {path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OpenTestability - Gate-Level Testability Analysis Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --parse -i design.v -o parsed_design.txt
  %(prog)s --scoap -i parsed_design.txt -o scoap_results.txt --json
  %(prog)s --dag -i parsed_design.json
  %(prog)s --graph -i design_dag.json
  %(prog)s --reconverge -i design_dag.json
        """
    )
    
    # Mode selection (mutually exclusive)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--parse', action='store_true', 
                     help="Parse Verilog netlist to internal format")
    mode.add_argument('--scoap', action='store_true', 
                     help="Compute SCOAP testability metrics")
    mode.add_argument('--dag', action='store_true', 
                     help="Build DAG representation from parsed netlist")
    mode.add_argument('--graph', action='store_true', 
                     help="Generate graph visualization from DAG")
    mode.add_argument('--reconverge', action='store_true', 
                     help="Detect reconvergent fanout structures")

    # Common arguments
    parser.add_argument('-i', '--input', required=True, 
                       help="Input filename (relative to appropriate data subdirectory)")
    parser.add_argument('-o', '--output', 
                       help="Output filename (required for parse/scoap modes)")
    parser.add_argument('--json', action='store_true', 
                       help="Also generate JSON output (for parse/scoap modes)")
    parser.add_argument('--verbose', action='store_true', 
                       help="Enable verbose output")
    
    args = parser.parse_args()

    # Validate required arguments
    if (args.parse or args.scoap) and not args.output:
        print("[✗] -o/--output is required for parse and scoap modes")
        sys.exit(1)

    paths = get_project_paths()

    try:
        if args.parse:
            # Parse Verilog netlist: data/input/ -> data/parsed/
            input_path = paths['input'] / args.input
            check_file(input_path)
            
            print("[2] Running Verilog parser...")
            output_path = run_parse(args.input, args.output)
            print(f"[3] Parsed netlist saved to: {output_path}")
            
            if args.json:
                print("[2] Converting to JSON format...")
                json_path = convert_txt_to_json(args.output)
                print(f"[3] JSON format saved to: {json_path}")

        elif args.scoap:
            # SCOAP analysis: data/parsed/ -> data/results/
            input_path = paths['parsed'] / args.input
            check_file(input_path)
            
            print("[2] Running SCOAP analysis...")
            output_path = run_scoap(args.input, args.output, json_flag=args.json)
            print(f"[3] SCOAP results saved to: {output_path}")
            
            if args.json:
                json_name = Path(args.output).stem + ".json"
                json_path = paths['results'] / json_name
                print(f"[3] SCOAP JSON saved to: {json_path}")

        elif args.dag:
            # DAG generation: data/parsed/ -> data/dag_output/
            input_path = paths['parsed'] / args.input
            check_file(input_path)
            
            print(f"[2] Building DAG from: {input_path}")
            output_path = create_dag_from_netlist(args.input)
            print(f"[3] DAG JSON saved to: {output_path}")

        elif args.graph:
            # Graph visualization: data/dag_output/ -> data/graphs/
            input_path = paths['dag_output'] / args.input
            check_file(input_path)
            
            print(f"[2] Rendering graph visualization from: {input_path}")
            output_path = visualize_gate_graph(args.input)
            print(f"[3] Graph visualization saved to: {output_path}")

        elif args.reconverge:
            # Reconvergence analysis: data/dag_output/ -> data/reconvergence_output/
            input_path = paths['dag_output'] / args.input
            check_file(input_path)
            
            print(f"[2] Analyzing reconvergent fanout from: {input_path}")
            output_path = analyze_reconvergence(args.input)
            print(f"[3] Reconvergence analysis saved to: {output_path}")

        print("[✓] Operation completed successfully!")

    except FileNotFoundError as e:
        print(f"[✗] File not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[✗] Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()