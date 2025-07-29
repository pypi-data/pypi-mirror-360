#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import argparse
import os
import time
import glob
import subprocess

# Check for completion requests BEFORE heavy imports
def is_completion_request():
    """Check if this is an argcomplete completion request"""
    return os.environ.get('_ARGCOMPLETE') == '1'

def get_dynamic_choices():
    """Simulate expensive dynamic choice generation"""
    # Simulate file system operations
    time.sleep(0.1)

    # Simulate subprocess calls
    try:
        subprocess.run(['echo', 'checking'], capture_output=True, timeout=0.05)
    except:
        pass

    # Simulate complex computation
    choices = []
    for i in range(1000):
        if i % 100 == 0:
            choices.append(f"option_{i}")

    return choices

def get_file_choices():
    """Simulate expensive file discovery"""
    time.sleep(0.05)

    # Simulate glob operations
    files = []
    for ext in ['*.txt', '*.json', '*.csv', '*.yaml', '*.yml']:
        try:
            files.extend(glob.glob(ext))
        except:
            pass

    return files[:10] if files else ['file1.txt', 'file2.json', 'file3.csv']

def get_network_choices():
    """Simulate expensive network operations"""
    time.sleep(0.08)

    # Simulate API calls
    try:
        # This would normally be a real API call
        return ['api1', 'api2', 'api3', 'api4', 'api5']
    except:
        return ['local1', 'local2', 'local3']

def create_complex_parser():
    """Create a very complex argument parser with expensive operations"""
    parser = argparse.ArgumentParser(
        description="A really slow CLI tool for testing tab completion with only argcomplete.",
        epilog="This tool is intentionally slow to demonstrate the need for fastargsnap."
    )

    # Global options with expensive validation
    parser.add_argument("--config", type=str, help="Configuration file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--debug", action="store_true", help="Debug mode")

    # Expensive dynamic choices
    dynamic_choices = get_dynamic_choices()
    parser.add_argument("--dynamic", choices=dynamic_choices, help="Dynamic choices")

    # File-based choices
    file_choices = get_file_choices()
    parser.add_argument("--file", choices=file_choices, help="File selection")

    # Network-based choices
    network_choices = get_network_choices()
    parser.add_argument("--api", choices=network_choices, help="API selection")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Complex subcommand: foo
    parser_foo = subparsers.add_parser("foo", help="Run foo command")
    parser_foo.add_argument("--bar", type=int, help="Bar value")
    parser_foo.add_argument("--baz", choices=["a", "b", "c"], help="Baz option")

    # Add more complex options
    for i in range(5):
        parser_foo.add_argument(f"--option{i}", type=str, help=f"Option {i}")

    # Expensive validation
    parser_foo.add_argument("--validate", type=str, help="Validation field")

    # Complex subcommand: data
    parser_data = subparsers.add_parser("data", help="Run data command")
    parser_data.add_argument("--file", type=str, help="Input file")
    parser_data.add_argument("--mode", choices=["fast", "slow"], help="Mode")

    # Add more complex options
    for i in range(3):
        parser_data.add_argument(f"--param{i}", type=str, help=f"Parameter {i}")

    # Expensive choices
    parser_data.add_argument("--format", choices=get_dynamic_choices()[:5], help="Output format")

    # Complex subcommand: process
    parser_process = subparsers.add_parser("process", help="Process data")
    parser_process.add_argument("--input", type=str, help="Input file")
    parser_process.add_argument("--output", type=str, help="Output file")
    parser_process.add_argument("--algorithm", choices=get_dynamic_choices()[:3], help="Algorithm")

    # Add nested subparsers
    process_subparsers = parser_process.add_subparsers(dest="process_type", help="Process type")

    # Nested subcommand: batch
    parser_batch = process_subparsers.add_parser("batch", help="Batch processing")
    parser_batch.add_argument("--size", type=int, help="Batch size")
    parser_batch.add_argument("--workers", type=int, help="Number of workers")

    # Nested subcommand: stream
    parser_stream = process_subparsers.add_parser("stream", help="Stream processing")
    parser_stream.add_argument("--buffer", type=int, help="Buffer size")
    parser_stream.add_argument("--timeout", type=float, help="Timeout")

    # Complex subcommand: analyze
    parser_analyze = subparsers.add_parser("analyze", help="Analyze data")
    parser_analyze.add_argument("--method", choices=["statistical", "ml", "deep"], help="Analysis method")
    parser_analyze.add_argument("--metrics", nargs="+", help="Metrics to compute")

    # Add more complex options with expensive validation
    for i in range(4):
        parser_analyze.add_argument(f"--config{i}", type=str, help=f"Configuration {i}")

    return parser

def handle_completion():
    """Handle completion requests - still expensive due to parser creation"""
    import argcomplete
    parser = create_complex_parser()
    argcomplete.autocomplete(parser)

def main():
    # Handle completion requests early
    if is_completion_request():
        handle_completion()
        return

    # Only do heavy imports for actual command execution
    import time
    # Simulate heavy imports
    import matplotlib.pyplot as plt  # noqa: F401
    import numpy as np  # noqa: F401
    import pandas as pd  # noqa: F401
    import sklearn  # noqa: F401
    import requests  # noqa: F401
    import click  # noqa: F401

    time.sleep(5)  # Simulate slow startup

    parser = create_complex_parser()

    # Always call argcomplete.autocomplete() as required by argcomplete docs
    import argcomplete
    argcomplete.autocomplete(parser)

    args = parser.parse_args()

    if args.command == "foo":
        print(f"Running foo with bar={args.bar}, baz={args.baz}")
    elif args.command == "data":
        print(f"Running data with file={args.file}, mode={args.mode}")
    elif args.command == "process":
        print(f"Running process with input={args.input}, output={args.output}")
    elif args.command == "analyze":
        print(f"Running analyze with method={args.method}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
