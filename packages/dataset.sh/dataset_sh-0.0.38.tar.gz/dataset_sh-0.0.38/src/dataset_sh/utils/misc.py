import json
import operator
import os
import re
import warnings


def readfile_or_default(fp, default=''):
    if os.path.exists(fp):
        with open(fp) as fd:
            return fd.read()
    return default


def count_slashes(input_string):
    dot_count = 0
    for char in input_string:
        if char == '/':
            dot_count += 1
    return dot_count


def is_name_legit(input_string):
    """
    Checks the validity of a given input string as per specified constraints.

    The function verifies if the input string:
    1. Starts with an alphabetic character (a-z or A-Z).
    2. Contains only alphanumeric characters (a-z, A-Z, 0-9), underscores ('_'), or
       hyphens ('-') after the initial character.

    Args:
        input_string: The string to check for validity.

    Returns:
        bool: True if the input string is valid according to the specified
        constraints, otherwise False.
    """
    return bool(re.match(r'^(?=[a-zA-Z])[a-zA-Z0-9_-]*$', input_string))


def parse_dataset_name(name: str):
    s_count = count_slashes(name)
    if s_count == 1:
        username, dataset_name = name.split('/')
    else:
        raise ValueError('dataset name must be [username]/[dataset_name]')

    if not is_name_legit(username) or not is_name_legit(dataset_name):
        raise ValueError('dataset name and store name must startswith a-zA-Z, and contains only [a-zA-Z0-9_-]')

    return username, dataset_name


def read_jsonl(line_stream):
    for line in line_stream:
        try:
            yield json.loads(line)
        except json.decoder.JSONDecodeError:
            pass


def id_function(x):
    return x


def get_tqdm(silent=False):
    if silent:
        return id_function
    try:
        import tqdm
        return tqdm.tqdm
    except ModuleNotFoundError as e:
        warnings.warn('cannot load module tqdm, maybe it is not installed ?', UserWarning)
        return id_function


def parse_tags(tag: str) -> list[str]:
    return [t.strip() for t in tag.split(',') if t.strip() != '']


def compare_version(version_str_x, op, version_str_y):
    """
    compare two version strings.
    Args:
        version_str_x: 0.0.1
        op:
        version_str_y: 0.0.2

    Returns:

    """
    ops = {
        "==": operator.eq,
        "<": operator.lt,
        ">": operator.gt,
        "<=": operator.le,
        ">=": operator.ge,
    }

    if op not in ops:
        raise ValueError('op must be one of [==, <, >, <=, >=]')

    def parse(v):
        return [int(part) for part in v.strip().split(".")]

    x_parts = parse(version_str_x)
    y_parts = parse(version_str_y)

    # Pad with zeros to equal length
    max_len = max(len(x_parts), len(y_parts))
    x_parts += [0] * (max_len - len(x_parts))
    y_parts += [0] * (max_len - len(y_parts))

    return ops[op](x_parts, y_parts)
