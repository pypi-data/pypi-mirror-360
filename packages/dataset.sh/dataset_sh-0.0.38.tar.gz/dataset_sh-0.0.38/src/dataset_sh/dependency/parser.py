import json
import re
from typing import Optional

from dataset_sh.clients.locator import DatasetLocator
from dataset_sh.dependency.model import DatasetDependencies, DatasetDependencyHostGroup, DatasetDependencyItem


def parse(content):
    ret = DatasetDependencies(**json.loads(content))
    for hg in ret.dependencies:
        for item in hg.datasets:
            DatasetLocator.from_str(item.source)
            if item.target:
                DatasetLocator.from_str(item.target)
    return ret


def parse_file(fp: str) -> DatasetDependencies:
    with open(fp) as f:
        return parse(f.read())

# class ParsingError(ValueError):
#     def __init__(self, msg):
#         super().__init__(msg)
#
#
# def parse(lines: str) -> DatasetDependencies:
#     result = DatasetDependencies()
#     current_host_group = DatasetDependencyHostGroup(host=DatasetConstants.CENTRAL_HOST)
#     for line in lines.split('\n'):
#         if is_host_line(line):
#             if len(current_host_group.datasets) > 0:
#                 result.datasets_by_host.append(current_host_group)
#             current_host_group = DatasetDependencyHostGroup(host=parse_host(line))
#         else:
#             item = parse_item(line)
#             if item is not None:
#                 current_host_group.datasets.append(item)
#     if len(current_host_group.datasets) > 0:
#         result.datasets_by_host.append(current_host_group)
#     return result
#
#
# def is_host_line(line: str):
#     return line.lower().startswith('host:')
#
#
# def parse_host(line: str):
#     if line.lower().startswith('host:'):
#         return line[5:].strip()
#     return None
#
#
# def is_valid_name(name):
#     pattern = r"^[a-zA-Z][a-zA-Z0-9_-]*/[a-zA-Z][a-zA-Z0-9_-]*$"
#     if re.match(pattern, name):
#         return True
#     return False
#
#
# def parse_kw_arg(kw_arg):
#     if '=' in kw_arg:
#         parts = kw_arg.split('=')
#         if len(parts) == 2:
#             k, w = parts
#             k = k.lower().strip()
#             if k in ['version', 'tag']:
#                 return k, w.strip()
#     else:
#         return None
#
#
# def parse_item(line: str) -> Optional[DatasetDependencyItem]:
#     line = line.strip()
#
#     if len(line) == 0 or line.startswith('#'):
#         return None
#
#     if '?' in line:
#         parts = line.split('?')
#         if len(parts) == 2:
#             dataset_fullname, kw_args = parts
#             item = DatasetDependencyItem(name=dataset_fullname.strip())
#             for kw_arg in kw_args.split('&'):
#                 kw = parse_kw_arg(kw_arg)
#                 if kw:
#                     k, w = parse_kw_arg(kw_arg)
#                     if k == 'version':
#                         item.version = w
#                     elif k == 'tag':
#                         item.tag = w
#             return item
#         raise ParsingError(f"Cannot parse dataset declaration: {line}")
#     else:
#         return DatasetDependencyItem(name=line)
