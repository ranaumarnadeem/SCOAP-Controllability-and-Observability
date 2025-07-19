#!/usr/bin/env python3
import argparse
import sys
from opentestability.parser import parse as run_parse
from opentestability.scoap import run as run_scoap

def main():
    p = argparse.ArgumentParser(description="OpenTestability CLI")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--parse', action='store_true', help="Parse a gate‑level netlist")
    mode.add_argument('--scoap', action='store_true', help="Compute SCOAP metrics on a parsed netlist")

    p.add_argument('-i', '--input',  required=True,
                   help="Input filename (in opentestability/netlist/ for parse, or parsednetlist/ for scoap)")
    p.add_argument('-o', '--output', required=True,
                   help="Output filename (in opentestability/parsednetlist/ for parse, or scoapout/ for scoap)")
    p.add_argument('--json', action='store_true',
                   help="(SCOAP only) also emit JSON output alongside text")

    args = p.parse_args()

    try:
        if args.parse:
            out_path = run_parse(args.input, args.output)
            print(f"[✓] Parsed → {out_path}")
        elif args.scoap:
            out_path = run_scoap(args.input, args.output, json_flag=args.json)
            print(f"[✓] SCOAP → {out_path}")
            if args.json:
                base, _ = out_path.rsplit('.', 1)
                print(f"[✓] SCOAP JSON → {base}.json")
    except Exception as e:
        print(f"[✗] Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
