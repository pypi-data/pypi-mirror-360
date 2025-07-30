"""
FastEntry - Fast Python CLI completion using automatic entrypoint generation
"""

import os
import sys
import json
import argparse
import argcomplete
from pathlib import Path
from typing import Optional, Dict, Any, List

from .core import FastEntry, generate_snapshot

__version__ = "0.1.1"

def enable_fast_completion(cli_file: str, output_file: Optional[str] = None,
                          snapshot_path: Optional[str] = None) -> str:
    """
    Enable fast completion by generating a lightweight entrypoint

    Args:
        cli_file: Path to the existing CLI file
        output_file: Optional output path (defaults to cli_file + '_completion.py')
        snapshot_path: Optional path for snapshot file

    Returns:
        Path to the generated entrypoint file
    """
    from .generator import EntrypointGenerator

    generator = EntrypointGenerator(cli_file, output_file, snapshot_path)
    return generator.generate()

def handle_completion_fast(snapshot_path: Optional[str] = None,
                          parser_func: Optional[str] = None):
    """
    Handle completion requests with minimal imports
    """
    try:
        # Try to use snapshot first
        if snapshot_path and os.path.exists(snapshot_path):
            fast_entry = FastEntry(snapshot_path)
            # Create minimal parser for completion
            parser = create_minimal_parser()
            if fast_entry.autocomplete(parser):
                return

        # Fallback to regular argcomplete
        import argcomplete
        parser = create_minimal_parser()
        argcomplete.autocomplete(parser)

    except Exception as e:
        # Final fallback: import the original CLI (slow but works)
        print(f"Fast completion failed: {e}", file=sys.stderr)
        # This will be handled by the lightweight entrypoint

def create_minimal_parser() -> argparse.ArgumentParser:
    """
    Create a minimal parser for completion requests
    """
    parser = argparse.ArgumentParser()
    # Add basic help option
    parser.add_argument('-h', '--help', action='help', help='show this help message and exit')
    return parser

# CLI command for generating entrypoints
def main():
    """CLI entry point for FastEntry"""
    parser = argparse.ArgumentParser(
        description="FastEntry - Enable fast completion for Python CLIs"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Enable command
    enable_parser = subparsers.add_parser(
        "enable",
        help="Enable fast completion for a CLI file"
    )
    enable_parser.add_argument(
        "cli_file",
        help="Path to the CLI file to enable completion for"
    )
    enable_parser.add_argument(
        "--output",
        help="Output file path (defaults to cli_file + '_completion.py')"
    )
    enable_parser.add_argument(
        "--snapshot",
        help="Path for snapshot file (defaults to cli_file + '_snapshot.json')"
    )

    # Generate snapshot command
    snapshot_parser = subparsers.add_parser(
        "snapshot",
        help="Generate snapshot for a CLI file"
    )
    snapshot_parser.add_argument(
        "cli_file",
        help="Path to the CLI file"
    )
    snapshot_parser.add_argument(
        "--output",
        help="Output snapshot path"
    )

    args = parser.parse_args()

    if args.command == "enable":
        output_path = enable_fast_completion(
            args.cli_file,
            args.output,
            args.snapshot
        )
        print(f"Generated lightweight entrypoint: {output_path}")
        print("Update your pyproject.toml to use this file as the entry point.")

    elif args.command == "snapshot":
        from .generator import generate_snapshot_for_file
        snapshot_path = generate_snapshot_for_file(args.cli_file, args.output)
        print(f"Generated snapshot: {snapshot_path}")

if __name__ == "__main__":
    main()
