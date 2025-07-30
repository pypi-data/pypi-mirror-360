import json
from typing import Dict, List, Optional, Any
import argparse

class FastEntry:
    """
    Fast argument completion using snapshot-based approach
    """
    def __init__(self, snapshot_path: str):
        self.snapshot_path = snapshot_path
        self.snapshot = None
        self._load_snapshot()

    def _load_snapshot(self):
        try:
            with open(self.snapshot_path, 'r') as f:
                self.snapshot = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.snapshot = None

    def autocomplete(self, parser: argparse.ArgumentParser) -> bool:
        if not self.snapshot:
            return False
        def complete_func(prefix, parsed_args, **kwargs):
            option_being_completed = kwargs.get('option_being_completed')
            return self._get_completions(prefix, parsed_args, option_being_completed=option_being_completed)
        setattr(parser, '_fastentry_completer', complete_func)
        return True

    def _get_completions(self, prefix: str, parsed_args: argparse.Namespace, option_being_completed: Optional[str] = None) -> List[str]:
        if not self.snapshot:
            return []
        command_path = self._get_command_path(parsed_args)
        node = self._find_node(command_path)
        if not node:
            return []
        completions = []
        # Option value completions
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
        # Positionals
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

    def _get_command_path(self, parsed_args: argparse.Namespace) -> List[str]:
        path = []
        if parsed_args is None:
            return path
        for attr in dir(parsed_args):
            if not attr.startswith('_') and hasattr(parsed_args, attr):
                value = getattr(parsed_args, attr)
                if isinstance(value, str) and value:
                    if attr.startswith('command_'):
                        try:
                            index = int(attr.split('_')[1])
                            while len(path) <= index:
                                path.append(None)
                            path[index] = value
                        except (ValueError, IndexError):
                            pass
                    elif attr in ['command', 'subcommand']:
                        if value not in path:
                            path.append(value)
        return [p for p in path if p is not None]

    def _find_node(self, command_path: List[str]) -> Optional[Dict[str, Any]]:
        if not self.snapshot:
            return None
        node = self.snapshot
        last_valid_node = node
        for cmd in command_path:
            found = False
            if node and 'subcommands' in node and node['subcommands']:
                for subcmd in node['subcommands']:
                    if subcmd['name'] == cmd:
                        node = subcmd
                        found = True
                        break
                if found:
                    if node and ('options' in node or 'subcommands' in node or 'positionals' in node):
                        last_valid_node = node
                    continue
            if node and 'positionals' in node and node['positionals']:
                for pos in node['positionals']:
                    if 'choices' in pos and pos['choices']:
                        for choice in pos['choices']:
                            if choice == cmd:
                                if node and 'subcommands' in node and node['subcommands']:
                                    for subcmd in node['subcommands']:
                                        if subcmd['name'] == choice:
                                            node = subcmd
                                            found = True
                                            break
                                if not found:
                                    node = {
                                        'name': choice,
                                        'options': node.get('options', []) if node else [],
                                        'positionals': node.get('positionals', []) if node else [],
                                        'subcommands': node.get('subcommands', []) if node else []
                                    }
                                    found = True
                                break
                        if found:
                            break
                if found:
                    if node and ('options' in node or 'subcommands' in node or 'positionals' in node):
                        last_valid_node = node
                    continue
            if not found:
                return last_valid_node
        return node

def generate_snapshot(parser: argparse.ArgumentParser, output_path: str):
    """Generate a complete snapshot of the parser structure including nested subcommands"""
    snapshot = _extract_parser_structure_recursive(parser)
    with open(output_path, 'w') as f:
        json.dump(snapshot, f, indent=2)
    print(f"Snapshot saved to {output_path}")

def _extract_parser_structure_recursive(parser: argparse.ArgumentParser) -> Dict[str, Any]:
    """Recursively extract the complete structure of a parser and all its subparsers"""
    structure = {
        'description': parser.description,
        'epilog': parser.epilog,
        'options': [],
        'positionals': [],
        'subcommands': []
    }

    # Extract options and positionals from current parser
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
            positional = {
                'name': action.dest,
                'help': action.help,
                'type': str(action.type) if action.type else None,
                'choices': list(action.choices) if action.choices else None,
                'nargs': str(action.nargs) if action.nargs else None
            }
            structure['positionals'].append(positional)

    # Recursively extract subcommands
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for name, subparser in action.choices.items():
                subcommand = _extract_parser_structure_recursive(subparser)
                subcommand['name'] = name
                structure['subcommands'].append(subcommand)

    return structure

def _extract_parser_structure(parser: argparse.ArgumentParser) -> Dict[str, Any]:
    """Legacy function for backward compatibility"""
    return _extract_parser_structure_recursive(parser)
