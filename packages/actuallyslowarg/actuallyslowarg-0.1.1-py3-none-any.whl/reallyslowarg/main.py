#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import argparse
import os
import time
import matplotlib.pyplot as plt  # noqa: F401
import numpy as np  # noqa: F401
import pandas as pd  # noqa: F401
import sklearn  # noqa: F401
import requests  # noqa: F401
import click  # noqa: F401

# Check for completion requests BEFORE heavy imports
def is_completion_request():
    """Check if this is an argcomplete completion request"""
    return os.environ.get('_ARGCOMPLETE') == '1'

def create_parser():
    """Create the argument parser - separated for snapshot generation"""
    parser = argparse.ArgumentParser(description="A really slow CLI tool for testing tab completion with only argcomplete.")
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

def handle_completion():
    """Handle completion requests without heavy imports - using only argcomplete"""
    import argcomplete
    parser = create_parser()
    argcomplete.autocomplete(parser)

def main():
    # Handle completion requests early
    if is_completion_request():
        handle_completion()
        return

    time.sleep(5)  # Simulate slow startup

    parser = create_parser()

    # Always call argcomplete.autocomplete() as required by argcomplete docs
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
    main()
