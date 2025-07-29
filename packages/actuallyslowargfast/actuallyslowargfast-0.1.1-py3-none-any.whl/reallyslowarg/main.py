#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import argparse
import os
import sys
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
        description="A really slow CLI tool for testing tab completion with fastargsnap.",
        epilog="This tool uses fastargsnap to demonstrate fast completion performance."
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

def create_minimal_parser():
    """Create a minimal parser for completion without expensive operations"""
    parser = argparse.ArgumentParser(
        description="A really slow CLI tool for testing tab completion with fastargsnap.",
        epilog="This tool uses fastargsnap to demonstrate fast completion performance."
    )

    # Global options without expensive validation
    parser.add_argument("--config", type=str, help="Configuration file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--debug", action="store_true", help="Debug mode")

    # Use static choices instead of expensive dynamic ones
    parser.add_argument("--dynamic", choices=["option_0", "option_100", "option_200", "option_300", "option_400", "option_500", "option_600", "option_700", "option_800", "option_900"], help="Dynamic choices")
    parser.add_argument("--file", choices=["file1.txt", "file2.json", "file3.csv"], help="File selection")
    parser.add_argument("--api", choices=["api1", "api2", "api3", "api4", "api5"], help="API selection")

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

    # Use static choices instead of expensive dynamic ones
    parser_data.add_argument("--format", choices=["option_0", "option_100", "option_200", "option_300", "option_400"], help="Output format")

    # Complex subcommand: process
    parser_process = subparsers.add_parser("process", help="Process data")
    parser_process.add_argument("--input", type=str, help="Input file")
    parser_process.add_argument("--output", type=str, help="Output file")
    parser_process.add_argument("--algorithm", choices=["option_0", "option_100", "option_200"], help="Algorithm")

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
    """Handle completion requests using fastargsnap for fast performance"""
    try:
        from fastargsnap import FastArgSnap

        snapshot_path = os.path.join(os.path.dirname(__file__), "reallyslowarg_snapshot.json")
        print(f"DEBUG: Looking for snapshot at: {snapshot_path}", file=sys.stderr)
        print(f"DEBUG: File exists: {os.path.exists(snapshot_path)}", file=sys.stderr)

        fast_snap = FastArgSnap(snapshot_path)
        print("DEBUG: FastArgSnap initialized", file=sys.stderr)

        # Use minimal parser for completion
        parser = create_minimal_parser()
        print("DEBUG: Minimal parser created", file=sys.stderr)

        result = fast_snap.autocomplete(parser)
        print(f"DEBUG: fast_snap.autocomplete returned: {result}", file=sys.stderr)

        if result:
            # Fast completion using snapshot
            print("DEBUG: Using fast completion", file=sys.stderr)
            return

        # Fallback to regular argcomplete
        print("DEBUG: Falling back to argcomplete", file=sys.stderr)
        import argcomplete
        argcomplete.autocomplete(parser)

    except ImportError as e:
        print(f"DEBUG: ImportError: {e}", file=sys.stderr)
        # If fastargsnap is not available, use regular argcomplete
        import argcomplete
        parser = create_minimal_parser()
        argcomplete.autocomplete(parser)
    except Exception as e:
        print(f"DEBUG: Exception: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        # Fallback to regular argcomplete
        import argcomplete
        parser = create_minimal_parser()
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
    try:
        from fastargsnap import FastArgSnap
        snapshot_path = os.path.join(os.path.dirname(__file__), "reallyslowarg_snapshot.json")
        fast_snap = FastArgSnap(snapshot_path)

        if not fast_snap.autocomplete(parser):
            # Fallback to regular argcomplete
            import argcomplete
            argcomplete.autocomplete(parser)
    except ImportError:
        # If fastargsnap is not available, use regular argcomplete
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
    # Generate snapshot if this is run directly
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-snapshot":
        from fastargsnap import generate_snapshot

        parser = create_minimal_parser()
        snapshot_path = os.path.join(os.path.dirname(__file__), "reallyslowarg_snapshot.json")
        generate_snapshot(parser, snapshot_path)
        print(f"Snapshot generated at: {snapshot_path}")
    else:
        main()
