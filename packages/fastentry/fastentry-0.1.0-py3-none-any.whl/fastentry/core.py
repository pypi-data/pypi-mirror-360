"""
Core functionality for FastEntry
"""

import json
from typing import Dict, List, Optional, Any
import argparse
import argcomplete


class FastEntry:
    """
    Fast argument completion using snapshot-based approach
    """

    def __init__(self, snapshot_path: str):
        """
        Initialize FastEntry with a snapshot file

        Args:
            snapshot_path: Path to the JSON snapshot file
        """
        self.snapshot_path = snapshot_path
        self.snapshot = None
        self._load_snapshot()

    def _load_snapshot(self):
        """Load the snapshot from JSON file"""
        try:
            with open(self.snapshot_path, 'r') as f:
                self.snapshot = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load snapshot from {self.snapshot_path}: {e}")
            self.snapshot = None

    def autocomplete(self, parser: argparse.ArgumentParser) -> bool:
        """
        Enable fast autocomplete for the parser

        Args:
            parser: The argparse parser to enable completion for

        Returns:
            True if snapshot was used successfully, False otherwise
        """
        if not self.snapshot:
            return False

        # Set up the completion function
        def complete_func(prefix, parsed_args, **kwargs):
            return self._get_completions(prefix, parsed_args)

        # Register the completion function
        argcomplete.autocomplete(parser, default_completer=complete_func)
        return True

    def _get_completions(self, prefix: str, parsed_args: argparse.Namespace) -> List[str]:
        """
        Get completions based on current input and parsed arguments

        Args:
            prefix: The current input prefix
            parsed_args: Already parsed arguments

        Returns:
            List of completion candidates
        """
        if not self.snapshot:
            return []

        # Get the current command path
        command_path = self._get_command_path(parsed_args)

        # Find the appropriate node in the snapshot
        node = self._find_node(command_path)
        if not node:
            return []

        # Get completions for this node
        completions = []

        # Add subcommands
        if 'subcommands' in node:
            for subcmd in node['subcommands']:
                if subcmd['name'].startswith(prefix):
                    completions.append(subcmd['name'])

        # Add options
        if 'options' in node:
            for option in node['options']:
                if option['name'].startswith(prefix):
                    completions.append(option['name'])

        # Add positional arguments
        if 'positionals' in node:
            for pos in node['positionals']:
                if 'choices' in pos:
                    for choice in pos['choices']:
                        if choice.startswith(prefix):
                            completions.append(choice)

        return completions

    def _get_command_path(self, parsed_args: argparse.Namespace) -> List[str]:
        """Get the current command path from parsed arguments"""
        path = []

        # Extract subcommand path from parsed args
        for attr in dir(parsed_args):
            if not attr.startswith('_') and hasattr(parsed_args, attr):
                value = getattr(parsed_args, attr)
                if isinstance(value, str) and value:
                    # This is a simple heuristic - in practice you'd need more sophisticated logic
                    if attr in ['command', 'subcommand']:
                        path.append(value)

        return path

    def _find_node(self, command_path: List[str]) -> Optional[Dict[str, Any]]:
        """Find the node in the snapshot tree for the given command path"""
        node = self.snapshot

        for cmd in command_path:
            if 'subcommands' in node:
                for subcmd in node['subcommands']:
                    if subcmd['name'] == cmd:
                        node = subcmd
                        break
                else:
                    return None
            else:
                return None

        return node


def generate_snapshot(parser: argparse.ArgumentParser, output_path: str):
    """
    Generate a snapshot of the argument parser structure

    Args:
        parser: The argparse parser to snapshot
        output_path: Path to save the JSON snapshot
    """
    snapshot = _extract_parser_structure(parser)

    with open(output_path, 'w') as f:
        json.dump(snapshot, f, indent=2)

    print(f"Snapshot saved to {output_path}")


def _extract_parser_structure(parser: argparse.ArgumentParser) -> Dict[str, Any]:
    """
    Extract the complete structure of an argparse parser

    Args:
        parser: The argparse parser

    Returns:
        Dictionary representation of the parser structure
    """
    structure = {
        'description': parser.description,
        'epilog': parser.epilog,
        'options': [],
        'positionals': [],
        'subcommands': []
    }

    # Extract options (arguments starting with -)
    for action in parser._actions:
        if action.option_strings:
            option = {
                'name': action.option_strings[0],
                'aliases': action.option_strings[1:] if len(action.option_strings) > 1 else [],
                'help': action.help,
                'type': str(action.type) if action.type else None,
                'choices': list(action.choices) if action.choices else None,
                'default': action.default,
                'required': action.required,
                'nargs': str(action.nargs) if action.nargs else None
            }
            structure['options'].append(option)
        else:
            # Positional argument
            positional = {
                'name': action.dest,
                'help': action.help,
                'type': str(action.type) if action.type else None,
                'choices': list(action.choices) if action.choices else None,
                'nargs': str(action.nargs) if action.nargs else None
            }
            structure['positionals'].append(positional)

    # Extract subcommands
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for name, subparser in action.choices.items():
                subcommand = {
                    'name': name,
                    'help': subparser.description,
                    'description': subparser.description,
                    'epilog': subparser.epilog,
                    'options': [],
                    'positionals': [],
                    'subcommands': []
                }

                # Extract subcommand options
                for subaction in subparser._actions:
                    if subaction.option_strings:
                        option = {
                            'name': subaction.option_strings[0],
                            'aliases': subaction.option_strings[1:] if len(subaction.option_strings) > 1 else [],
                            'help': subaction.help,
                            'type': str(subaction.type) if subaction.type else None,
                            'choices': list(subaction.choices) if subaction.choices else None,
                            'default': subaction.default,
                            'required': subaction.required,
                            'nargs': str(subaction.nargs) if subaction.nargs else None
                        }
                        subcommand['options'].append(option)
                    else:
                        # Subcommand positional argument
                        positional = {
                            'name': subaction.dest,
                            'help': subaction.help,
                            'type': str(subaction.type) if subaction.type else None,
                            'choices': list(subaction.choices) if subaction.choices else None,
                            'nargs': str(subaction.nargs) if subaction.nargs else None
                        }
                        subcommand['positionals'].append(positional)

                structure['subcommands'].append(subcommand)

    return structure
