#!/usr/bin/env python3
import argparse
import sys
import subprocess
import os


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CODES_DIR  = os.path.join(SCRIPT_DIR, 'codes')

from codes.parser import parse as run_parse
from codes.scoap import run as run_scoap


def check_file(path):
    if not os.path.exists(path):
        print(f"[✗] Input file not found: {path}")
        sys.exit(1)
    print(f"[1] Found input file at: {path}")


def main():
    p = argparse.ArgumentParser(description="OpenTestability CLI")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--parse', action='store_true', help="Parse netlist to text")
    mode.add_argument('--scoap', action='store_true', help="Compute SCOAP metrics")
    mode.add_argument('--dag', action='store_true', help="Build DAG JSON from parsed netlist")
    mode.add_argument('--graph', action='store_true', help="Render graph PNG from DAG JSON")
    mode.add_argument('--reconverge', action='store_true', help="Detect reconvergence")

    p.add_argument('-i', '--input', required=True, help="Input filename (no path)")
    p.add_argument('-o', '--output', help="Output filename (required for parse/scoap)")
    p.add_argument('--json', action='store_true', help="(parse/scoap) also emit JSON output")
    args = p.parse_args()

    # parse/scoap require -o
    if (args.parse or args.scoap) and not args.output:
        print("[✗] -o/--output is required for parse and scoap modes")
        sys.exit(1)

    try:
        if args.parse:
            netlist_dir = os.path.join(CODES_DIR, 'netlist')
            in_path = os.path.join(netlist_dir, args.input)
            check_file(in_path)
            print("[2] Running parser...")
            out_path = run_parse(args.input, args.output)
            print(f"[3] Parsed TXT output at: {out_path}")
            if args.json:
                json_conv = os.path.join(CODES_DIR, 'json_conv.py')
                print("[2] Converting TXT to JSON...")
                subprocess.run(['python3', json_conv, out_path], check=True)
                base, _ = os.path.splitext(out_path)
                print(f"[3] JSON output at: {base}.json")

        elif args.scoap:
            parsed_dir = os.path.join(CODES_DIR, 'parsednetlist')
            in_path = os.path.join(parsed_dir, args.input)
            check_file(in_path)
            print("[2] Running SCOAP...")
            out_path = run_scoap(args.input, args.output, json_flag=args.json)
            print(f"[3] SCOAP TXT at: {out_path}")
            if args.json:
                base, _ = os.path.splitext(out_path)
                print(f"[3] SCOAP JSON at: {base}.json")

        elif args.dag:
            # input from codes/parsednetlist, output to codes/dagoutput
            parsed_dir = os.path.join(CODES_DIR, 'parsednetlist')
            in_path = os.path.join(parsed_dir, args.input)
            check_file(in_path)
            print(f"[2] Building DAG JSON from: {in_path}...")
            dag_py = os.path.join(CODES_DIR, 'dag.py')
            subprocess.run(['python3', dag_py, args.input], check=True)
            output_path = os.path.join(CODES_DIR, 'dagoutput', f"{os.path.splitext(args.input)[0]}_dag.json")
            print(f"[3] DAG JSON written to: {output_path}")

        elif args.graph:
            # input from codes/dagoutput, output to codes/graph
            dag_dir = os.path.join(CODES_DIR, 'dagoutput')
            in_path = os.path.join(dag_dir, args.input)
            check_file(in_path)
            print(f"[2] Rendering graph PNG from: {in_path}...")
            graph_py = os.path.join(CODES_DIR, 'graph.py')
            subprocess.run(['python3', graph_py, args.input], check=True)
            output_png = os.path.join(CODES_DIR, 'graph', f"{os.path.splitext(args.input)[0]}_graph.png")
            print(f"[3] Graph PNG at: {output_png}")

        elif args.reconverge:
            # input from codes/dagoutput, output to codes/reconvergence
            dag_dir = os.path.join(CODES_DIR, 'dagoutput')
            in_path = os.path.join(dag_dir, args.input)
            check_file(in_path)
            print(f"[2] Detecting reconvergence from: {in_path}...")
            reconv_py = os.path.join(CODES_DIR, 'reconverge.py')
            subprocess.run(['python3', reconv_py, args.input], check=True)
            output_json = os.path.join(CODES_DIR, 'reconvergence', f"{os.path.splitext(args.input)[0]}_reconv.json")
            print(f"[3] Reconvergence JSON at: {output_json}")

    except subprocess.CalledProcessError as e:
        print(f"[✗] Subprocess failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[✗] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

