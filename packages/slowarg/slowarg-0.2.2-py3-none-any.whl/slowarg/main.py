import time
# Simulate heavy imports
import matplotlib.pyplot as plt  # noqa: F401
import numpy as np  # noqa: F401
import pandas as pd  # noqa: F401
import sklearn  # noqa: F401
import requests  # noqa: F401
import click  # noqa: F401

time.sleep(5)  # Simulate slow startup

import argparse
import os
import sys
from fastargsnap import FastArgSnap

def create_parser():
    """Create the argument parser - separated for snapshot generation"""
    parser = argparse.ArgumentParser(description="A slow CLI tool for testing tab completion.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: foo
    parser_foo = subparsers.add_parser("foo", help="Run foo command")
    parser_foo.add_argument("--bar", type=int, help="Bar value")
    parser_foo.add_argument("--baz", choices=["a", "b", "c"], help="Baz option")

    # Subcommand: data
    parser_data = subparsers.add_parser("data", help="Run data command")
    parser_data.add_argument("--file", type=str, help="Input file")
    parser_data.add_argument("--mode", choices=["fast", "slow"], help="Mode")

    return parser

def main():
    parser = create_parser()

    # Try to use fastargsnap for completions
    snapshot_path = os.path.join(os.path.dirname(__file__), "slowarg_snapshot.json")
    fast_snap = FastArgSnap(snapshot_path)

    if not fast_snap.autocomplete(parser):
        # Fallback to regular argcomplete if snapshot not available
        import argcomplete
        argcomplete.autocomplete(parser)

    args = parser.parse_args()

    if args.command == "foo":
        print(f"Running foo with bar={args.bar}, baz={args.baz}")
    elif args.command == "data":
        print(f"Running data with file={args.file}, mode={args.mode}")
    else:
        parser.print_help()

if __name__ == "__main__":
    # Generate snapshot if this is run directly
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-snapshot":
        from fastargsnap import generate_snapshot

        parser = create_parser()
        snapshot_path = os.path.join(os.path.dirname(__file__), "slowarg_snapshot.json")
        generate_snapshot(parser, snapshot_path)
        print(f"Snapshot generated at: {snapshot_path}")
    else:
        main()
