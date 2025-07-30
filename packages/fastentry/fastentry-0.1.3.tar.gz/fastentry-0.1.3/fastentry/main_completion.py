#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
"""
Main completion handler for FastEntry

This module provides the entry point for fast completion using snapshots.
It implements smart prefix extraction and command path extraction.
"""

import os
import sys
import json
import argparse
from typing import List, Optional, Dict, Any

def is_completion_request():
    """Check if this is an argcomplete completion request"""
    return os.environ.get('_ARGCOMPLETE') == '1'

def handle_completion_fast(snapshot_path: str):
    """Handle completion requests with minimal imports"""
    try:
        # Load snapshot
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

    except Exception:
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
                                node = {
                                    'name': choice,
                                    'options': node.get('options', []),
                                    'positionals': node.get('positionals', []),
                                    'subcommands': node.get('subcommands', [])
                                }
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

def create_mock_args(command_path: List[str]) -> argparse.Namespace:
    """Create mock args for the given command path"""
    args = argparse.Namespace()

    # Set command attributes
    for i, cmd in enumerate(command_path):
        setattr(args, f'command_{i}', cmd)

    return args

def main():
    """Main entry point for completion"""
    if is_completion_request():
        # Get snapshot path from environment or use default
        snapshot_path = os.environ.get('FASTENTRY_SNAPSHOT_PATH', 'snapshot.json')
        handle_completion_fast(snapshot_path)
    else:
        # This should not be called directly
        print("This script is for completion only", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
