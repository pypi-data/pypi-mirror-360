"""
Entrypoint generator for FastEntry

This module handles automatic generation of lightweight completion entrypoints
and snapshots for existing CLI applications.
"""

import sys
import ast
import json
import importlib.util
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

from .core import generate_snapshot


class EntrypointGenerator:
    """
    Generates lightweight completion entrypoints for CLI applications
    """

    def __init__(self, cli_file: str, output_file: Optional[str] = None,
                 snapshot_path: Optional[str] = None):
        """
        Initialize the generator

        Args:
            cli_file: Path to the original CLI file
            output_file: Optional output path for the entrypoint
            snapshot_path: Optional path for the snapshot file
        """
        self.cli_file = Path(cli_file)
        self.output_file = Path(output_file) if output_file else self._get_default_output_path()
        self.snapshot_path = Path(snapshot_path) if snapshot_path else self._get_default_snapshot_path()

    def _get_default_output_path(self) -> Path:
        """Get default output path for the entrypoint"""
        return self.cli_file.parent / f"{self.cli_file.stem}_completion.py"

    def _get_default_snapshot_path(self) -> Path:
        """Get default snapshot path"""
        return self.cli_file.parent / f"{self.cli_file.stem}_snapshot.json"

    def generate(self) -> str:
        """
        Generate the lightweight entrypoint

        Returns:
            Path to the generated entrypoint file
        """
        # First, generate the snapshot
        self._generate_snapshot()

        # Then generate the entrypoint
        self._generate_entrypoint()

        return str(self.output_file)

    def _generate_snapshot(self):
        """Generate snapshot from the CLI file"""
        try:
            generate_snapshot_for_file(str(self.cli_file), str(self.snapshot_path))
        except Exception as e:
            print(f"Warning: Could not generate snapshot: {e}", file=sys.stderr)
            # Continue without snapshot - will fall back to regular argcomplete

    def _generate_entrypoint(self):
        """Generate the lightweight entrypoint file"""
        # Analyze the CLI file to extract module and function names
        module_name, main_function = self._extract_cli_info()

        # Generate the entrypoint code
        entrypoint_code = self._generate_entrypoint_code(module_name, main_function)

        # Write the entrypoint file
        with open(self.output_file, 'w') as f:
            f.write(entrypoint_code)

        # Make it executable
        self.output_file.chmod(0o755)

    def _extract_cli_info(self) -> Tuple[str, str]:
        """
        Extract module name and main function from CLI file

        Returns:
            Tuple of (module_name, main_function)
        """
        try:
            # Read the CLI file
            with open(self.cli_file, 'r') as f:
                content = f.read()

            # Parse the AST
            tree = ast.parse(content)

            # Look for main function
            main_function = "main"
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name == "main":
                        main_function = "main"
                        break
                    elif node.name == "__main__":
                        main_function = "__main__"
                        break

            # Determine the proper import path
            # If the file is in a package directory (has __init__.py), use package.module format
            module_name = self._determine_import_path()

            return module_name, main_function

        except Exception as e:
            print(f"Warning: Could not analyze CLI file: {e}", file=sys.stderr)
            # Fallback to common patterns
            return self.cli_file.stem, "main"

    def _determine_import_path(self) -> str:
        """
        Determine the proper import path for the CLI file

        Returns:
            Import path (e.g., 'slowcli.main' for slowcli/main.py)
        """
        # Check if we're in a package structure
        current_dir = self.cli_file.parent
        package_parts = []

        print(f"DEBUG: CLI file: {self.cli_file}", file=sys.stderr)
        print(f"DEBUG: Starting from directory: {current_dir}", file=sys.stderr)

        # Walk up the directory tree looking for __init__.py files
        while current_dir.exists():
            # Check if this directory is a package
            init_file = current_dir / "__init__.py"
            print(f"DEBUG: Checking {current_dir} for __init__.py: {init_file.exists()}", file=sys.stderr)
            if init_file.exists():
                package_parts.insert(0, current_dir.name)
                print(f"DEBUG: Added package part: {current_dir.name}", file=sys.stderr)
            else:
                # Stop at the first non-package directory
                print(f"DEBUG: Stopping at non-package directory: {current_dir}", file=sys.stderr)
                break

            # Move up one level
            current_dir = current_dir.parent

            # Safety check to avoid infinite loop
            if current_dir == current_dir.parent:
                print("DEBUG: Reached root directory", file=sys.stderr)
                break

        # Add the module name
        if package_parts:
            package_parts.append(self.cli_file.stem)
            result = ".".join(package_parts)
            print(f"DEBUG: Final import path: {result}", file=sys.stderr)
            return result
        else:
            # Not in a package, use just the module name
            result = self.cli_file.stem
            print(f"DEBUG: No package found, using: {result}", file=sys.stderr)
            return result

    def _generate_entrypoint_code(self, module_name: str, main_function: str) -> str:
        """
        Generate the entrypoint code using the improved main_completion.py template

        Args:
            module_name: Name of the module to import
            main_function: Name of the main function

        Returns:
            Generated entrypoint code
        """
        # Use the determined import path
        import_path = module_name

        entrypoint_code = f'''#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
"""
Lightweight completion entrypoint for {self.cli_file.name}
Generated by FastEntry - DO NOT EDIT MANUALLY
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Any

def is_completion_request():
    """Check if this is an argcomplete completion request"""
    return os.environ.get('_ARGCOMPLETE') == '1'

def handle_completion_fast():
    """Handle completion requests with minimal imports using improved logic"""
    try:
        # Load snapshot
        snapshot_path = "{self.snapshot_path}"
        with open(snapshot_path, 'r') as f:
            snapshot = json.load(f)

        # Get completion words from environment
        words = os.environ.get('COMP_WORDS', '').split()
        if not words:
            return

        # Extract command path (stop at options)
        command_path = []
        for w in words[1:]:  # Skip the command name
            if w.startswith('-'):
                break
            command_path.append(w)

        # Smart prefix extraction
        last_option = None
        prefix = ''
        option_being_completed = None

        # Walk through words to find the last option and set prefix
        i = 1  # skip the command name
        while i < len(words):
            word = words[i]
            if word.startswith('-'):
                last_option = word
                if i == len(words) - 1:
                    # Cursor is after an option, completing its value
                    prefix = ''
                    option_being_completed = last_option
                    break
                elif i == len(words) - 2:
                    # Cursor is after a value for an option
                    prefix = words[-1]
                    option_being_completed = last_option
                    break
            i += 1

        # If no option context found, use the last word as prefix
        if not option_being_completed:
            prefix = words[-1] if len(words) > 1 else ''

        # Find the appropriate node in the snapshot
        node = find_node(snapshot, command_path)
        if not node:
            return

        # Get completions
        completions = get_completions(node, prefix, option_being_completed)

        # Output completions
        for completion in completions:
            print(completion)

    except Exception as e:
        # Fallback to regular argcomplete
        import argcomplete
        parser = argparse.ArgumentParser()
        parser.add_argument('-h', '--help', action='help', help='show this help message and exit')
        argcomplete.autocomplete(parser)

def find_node(snapshot: Dict[str, Any], command_path: List[str]) -> Optional[Dict[str, Any]]:
    """Find the appropriate node in the snapshot for the given command path"""
    node = snapshot
    last_valid_node = node  # Fallback mechanism

    for cmd in command_path:
        found = False

        # Try subcommands first
        if 'subcommands' in node and node['subcommands']:
            for subcmd in node['subcommands']:
                if subcmd['name'] == cmd:
                    node = subcmd
                    found = True
                    break
            if found:
                if node and ('options' in node or 'subcommands' in node or 'positionals' in node):
                    last_valid_node = node
                continue

        # Try positionals with choices
        if 'positionals' in node and node['positionals']:
            for pos in node['positionals']:
                if 'choices' in pos and pos['choices']:
                    for choice in pos['choices']:
                        if choice == cmd:
                            # Create virtual node for this choice
                            if 'subcommands' in node and node['subcommands']:
                                for subcmd in node['subcommands']:
                                    if subcmd['name'] == choice:
                                        node = subcmd
                                        found = True
                                        break
                            if not found:
                                # Create virtual node
                                node = {{
                                    'name': choice,
                                    'options': node.get('options', []),
                                    'positionals': node.get('positionals', []),
                                    'subcommands': node.get('subcommands', [])
                                }}
                                found = True
                            break
                    if found:
                        break
            if found:
                if node and ('options' in node or 'subcommands' in node or 'positionals' in node):
                    last_valid_node = node
                continue

        # Fallback to last valid node
        if not found:
            return last_valid_node

    return node

def get_completions(node: Dict[str, Any], prefix: str, option_being_completed: Optional[str] = None) -> List[str]:
    """Get completions for the given node and prefix"""
    completions = []

    # If completing a value for an option, suggest its choices
    if option_being_completed and 'options' in node:
        for option in node['options']:
            if option_being_completed in [option['name']] + option.get('aliases', []):
                if option.get('choices'):
                    for choice in option['choices']:
                        if prefix == '' or str(choice).startswith(prefix):
                            completions.append(str(choice))
                    return completions

    # Subcommands
    if 'subcommands' in node:
        for subcmd in node['subcommands']:
            if prefix == '' or subcmd['name'].startswith(prefix):
                completions.append(subcmd['name'])

    # Options
    if 'options' in node:
        for option in node['options']:
            if prefix == '' or option['name'].startswith(prefix):
                completions.append(option['name'])

    # Positionals with choices
    if 'positionals' in node:
        for pos in node['positionals']:
            if 'choices' in pos and pos['choices']:
                for choice in pos['choices']:
                    if prefix == '' or choice.startswith(prefix):
                        completions.append(choice)

    # Remove duplicates
    seen = set()
    unique_completions = []
    for completion in completions:
        if completion not in seen:
            seen.add(completion)
            unique_completions.append(completion)

    return unique_completions

def main():
    """Main entry point"""
    if is_completion_request():
        handle_completion_fast()
        return

    # Import and run the original CLI
    from {import_path} import {main_function}
    {main_function}()

if __name__ == "__main__":
    main()
'''
        return entrypoint_code


def generate_snapshot_for_file(cli_file: str, output_path: Optional[str] = None) -> str:
    """
    Generate a snapshot for a CLI file

    Args:
        cli_file: Path to the CLI file
        output_path: Optional output path for the snapshot

    Returns:
        Path to the generated snapshot file
    """
    if output_path is None:
        output_path = str(Path(cli_file).with_suffix('.json'))

    try:
        # Determine if this is a package module and get the import path
        cli_path = Path(cli_file)
        module_name = _determine_module_import_path(cli_path)

        # Import the CLI module
        if module_name != cli_path.stem:
            # This is a package module, import it properly
            print(f"DEBUG: Importing package module: {module_name}", file=sys.stderr)
            module = importlib.import_module(module_name)
        else:
            # This is a standalone script, use file-based import
            print(f"DEBUG: Importing standalone script: {cli_file}", file=sys.stderr)
            spec = importlib.util.spec_from_file_location("cli_module", cli_file)
            if spec is None:
                raise ImportError(f"Could not create spec for {cli_file}")
            module = importlib.util.module_from_spec(spec)
            if spec.loader is None:
                raise ImportError(f"Could not get loader for {cli_file}")
            spec.loader.exec_module(module)

        # Look for parser or main function
        parser = None

        # Try to find parser
        if hasattr(module, 'parser'):
            parser = module.parser
        elif hasattr(module, 'create_parser'):
            parser = module.create_parser()
        elif hasattr(module, 'main'):
            # Try to extract parser from main function
            # This is a simplified approach
            print(f"Warning: Could not find parser in {cli_file}")
            print("You may need to manually create a parser and call generate_snapshot()")
            return output_path
        else:
            print(f"Error: Could not find parser in {cli_file}")
            return output_path

        # Generate snapshot
        generate_snapshot(parser, output_path)
        print(f"Successfully generated snapshot for {cli_file}")

    except Exception as e:
        print(f"Error generating snapshot for {cli_file}: {e}")
        # Create a minimal snapshot
        minimal_snapshot = {
            "description": f"Generated snapshot for {cli_file}",
            "options": [],
            "positionals": [],
            "subcommands": []
        }

        with open(output_path, 'w') as f:
            json.dump(minimal_snapshot, f, indent=2)

    return output_path


def _determine_module_import_path(cli_path: Path) -> str:
    """
    Determine the proper import path for a CLI file

    Args:
        cli_path: Path to the CLI file

    Returns:
        Import path (e.g., 'slowcli.main' for slowcli/main.py)
    """
    # Check if we're in a package structure
    current_dir = cli_path.parent
    package_parts = []

    # Walk up the directory tree looking for __init__.py files
    while current_dir.exists():
        # Check if this directory is a package
        init_file = current_dir / "__init__.py"
        if init_file.exists():
            package_parts.insert(0, current_dir.name)
        else:
            # Stop at the first non-package directory
            break

        # Move up one level
        current_dir = current_dir.parent

        # Safety check to avoid infinite loop
        if current_dir == current_dir.parent:
            break

    # Add the module name
    if package_parts:
        package_parts.append(cli_path.stem)
        return ".".join(package_parts)
    else:
        # Not in a package, use just the module name
        return cli_path.stem


def analyze_cli_file(cli_file: str) -> Dict[str, Any]:
    """
    Analyze a CLI file to extract information

    Args:
        cli_file: Path to the CLI file

    Returns:
        Dictionary with analysis results
    """
    try:
        with open(cli_file, 'r') as f:
            content = f.read()

        tree = ast.parse(content)

        analysis = {
            'imports': [],
            'functions': [],
            'classes': [],
            'has_main': False,
            'has_argparse': False,
            'has_argcomplete': False
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    analysis['imports'].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    analysis['imports'].append(f"{module}.{alias.name}")
            elif isinstance(node, ast.FunctionDef):
                analysis['functions'].append(node.name)
                if node.name == 'main':
                    analysis['has_main'] = True
            elif isinstance(node, ast.ClassDef):
                analysis['classes'].append(node.name)

        # Check for specific imports
        analysis['has_argparse'] = any('argparse' in imp for imp in analysis['imports'])
        analysis['has_argcomplete'] = any('argcomplete' in imp for imp in analysis['imports'])

        return analysis

    except Exception as e:
        print(f"Error analyzing {cli_file}: {e}")
        return {
            'imports': [],
            'functions': [],
            'classes': [],
            'has_main': False,
            'has_argparse': False,
            'has_argcomplete': False
        }
