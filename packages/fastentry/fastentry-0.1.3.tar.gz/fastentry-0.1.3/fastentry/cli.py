"""
Command-line interface for FastEntry
"""

import argparse
import sys
from pathlib import Path

from . import enable_fast_completion
from .generator import generate_snapshot_for_file


def main():
    """Main CLI entry point for FastEntry"""
    parser = argparse.ArgumentParser(
        description="FastEntry - Enable fast completion for Python CLIs",
        epilog="For more information, visit: https://github.com/example/fastentry"
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
    enable_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files"
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

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a CLI file to understand its structure"
    )
    analyze_parser.add_argument(
        "cli_file",
        help="Path to the CLI file to analyze"
    )

    args = parser.parse_args()

    if args.command == "enable":
        _handle_enable(args)
    elif args.command == "snapshot":
        _handle_snapshot(args)
    elif args.command == "analyze":
        _handle_analyze(args)


def _handle_enable(args):
    """Handle the enable command"""
    cli_file = Path(args.cli_file)

    if not cli_file.exists():
        print(f"Error: CLI file '{cli_file}' does not exist", file=sys.stderr)
        sys.exit(1)

    # Check if output files already exist
    output_file = args.output or f"{cli_file.stem}_completion.py"
    snapshot_file = args.snapshot or f"{cli_file.stem}_snapshot.json"

    if not args.force:
        if Path(output_file).exists():
            print(f"Error: Output file '{output_file}' already exists. Use --force to overwrite.", file=sys.stderr)
            sys.exit(1)
        if Path(snapshot_file).exists():
            print(f"Error: Snapshot file '{snapshot_file}' already exists. Use --force to overwrite.", file=sys.stderr)
            sys.exit(1)

    try:
        print(f"Enabling fast completion for {cli_file}...")
        output_path = enable_fast_completion(
            str(cli_file),
            args.output,
            args.snapshot
        )
        print(f"✅ Generated lightweight entrypoint: {output_path}")
        print()
        print("Next steps:")
        print(f"1. Update your pyproject.toml to use '{output_path}' as the entry point")
        print("2. Test the completion by running your CLI with tab completion")
        print("3. If you encounter issues, the system will fall back to the original CLI")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _handle_snapshot(args):
    """Handle the snapshot command"""
    cli_file = Path(args.cli_file)

    if not cli_file.exists():
        print(f"Error: CLI file '{cli_file}' does not exist", file=sys.stderr)
        sys.exit(1)

    try:
        print(f"Generating snapshot for {cli_file}...")
        snapshot_path = generate_snapshot_for_file(str(cli_file), args.output)
        print(f"✅ Generated snapshot: {snapshot_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _handle_analyze(args):
    """Handle the analyze command"""
    from .generator import analyze_cli_file

    cli_file = Path(args.cli_file)

    if not cli_file.exists():
        print(f"Error: CLI file '{cli_file}' does not exist", file=sys.stderr)
        sys.exit(1)

    try:
        print(f"Analyzing {cli_file}...")
        analysis = analyze_cli_file(str(cli_file))

        print("\n📊 Analysis Results:")
        print("=" * 50)

        print(f"📁 File: {cli_file}")
        print(f"🔧 Has main function: {'✅' if analysis['has_main'] else '❌'}")
        print(f"📋 Has argparse: {'✅' if analysis['has_argparse'] else '❌'}")
        print(f"⚡ Has argcomplete: {'✅' if analysis['has_argcomplete'] else '❌'}")

        if analysis['functions']:
            print(f"\n🔧 Functions found: {', '.join(analysis['functions'])}")

        if analysis['classes']:
            print(f"\n🏗️  Classes found: {', '.join(analysis['classes'])}")

        if analysis['imports']:
            print(f"\n📦 Imports found: {', '.join(analysis['imports'][:10])}")
            if len(analysis['imports']) > 10:
                print(f"   ... and {len(analysis['imports']) - 10} more")

        print("\n💡 Recommendations:")
        if not analysis['has_argparse']:
            print("   ❌ No argparse found - this CLI may not be compatible")
        elif not analysis['has_argcomplete']:
            print("   ⚠️  No argcomplete found - completion may not work")
        else:
            print("   ✅ CLI appears to be compatible with FastEntry")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
