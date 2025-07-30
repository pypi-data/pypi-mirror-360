import copy
from dateutil import parser
import subprocess
import sys
import time
import click

def to_tabular(lines: str, header: str = None, dashed_line = False):
    return lines_to_tabular(lines.split('\n'), header, dashed_line)

def lines_to_tabular(lines: list[str], header: str = None, dashed_line = False, separator = ' '):
    maxes = []
    nls = []

    def format_line(line: str):
        nl = []
        words = line.split(separator)
        for i, word in enumerate(words):
            nl.append(word.ljust(maxes[i], ' '))
        nls.append('  '.join(nl))

    all_lines = lines
    if header:
        all_lines = [header] + lines

    for line in all_lines:
        words = line.split(separator)
        for i, word in enumerate(words):
            lw = len(word)
            if len(maxes) <= i:
                maxes.append(lw)
            elif maxes[i] < lw:
                maxes[i] = lw

    if header:
        format_line(header)
        if dashed_line:
            nls.append(''.ljust(sum(maxes) + (len(maxes) - 1) * 2, '-'))
    for line in lines:
        format_line(line)

    return '\n'.join(nls)

def convert_seconds(total_seconds_float):
    total_seconds_int = int(total_seconds_float)  # Convert float to integer seconds

    hours = total_seconds_int // 3600
    remaining_seconds_after_hours = total_seconds_int % 3600

    minutes = remaining_seconds_after_hours // 60
    seconds = remaining_seconds_after_hours % 60

    return hours, minutes, seconds

def epoch(timestamp_string: str):
    return parser.parse(timestamp_string).timestamp()

def log(s = None):
    if s:
        click.echo(s)
    else:
        print()

def log2(s = None):
    if s:
        click.echo(s, err=True)
    else:
        print(file=sys.stderr)

def elapsed_time(start_time: float):
    end_time = time.time()
    elapsed_time = end_time - start_time
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)

    return f"{hours:02}:{minutes:02}:{seconds:02}"

def strip(lines):
    return '\n'.join([line.strip(' ') for line in lines.split('\n')]).strip('\n')

def deep_merge_dicts(dict1, dict2):
    """
    Recursively merges dict2 into dict1.
    If a key exists in both dictionaries and its value is a dictionary,
    the function recursively merges those nested dictionaries.
    Otherwise, values from dict2 overwrite values in dict1.
    """
    merged_dict = dict1.copy()  # Create a copy to avoid modifying original dict1

    for key, value in dict2.items():
        if key in merged_dict and isinstance(merged_dict[key], dict) and isinstance(value, dict):
            # If both values are dictionaries, recursively merge them
            merged_dict[key] = deep_merge_dicts(merged_dict[key], value)
        elif key not in merged_dict or value:
            # Otherwise, overwrite or add the value from dict2
            merged_dict[key] = value
    return merged_dict

def get_deep_keys(d, current_path=""):
    """
    Recursively collects all combined keys (paths) from a deep dictionary.

    Args:
        d (dict): The dictionary to traverse.
        current_path (str): The current path of keys, used for recursion.

    Returns:
        list: A list of strings, where each string represents a combined key path
            (e.g., "key1.subkey1.nestedkey").
    """
    keys = []
    for k, v in d.items():
        new_path = f"{current_path}.{k}" if current_path else str(k)
        if isinstance(v, dict):
            keys.extend(get_deep_keys(v, new_path))
        else:
            keys.append(new_path)
    return keys

def display_help(replace_arg = False):
    args = copy.copy(sys.argv)
    if replace_arg:
        args[len(args) - 1] = '--help'
    else:
        args.extend(['--help'])
    subprocess.run(args)