from typing import Union, Optional

from .core import EnumEntry, FieldType, PydanticFieldDefinition, EnumDefinition, ClassDefinition, \
    DatasetSchema
from .constants import SUPPORTED_TYPES


def doc_to_doc_str(doc_or_none: Optional[str]) -> Optional[str]:
    if doc_or_none is None:
        return None
    else:

        indented_doc_str = '\n'.join(
            [f"    {line}" for line in doc_or_none.split('\n')]
        )
        return "\n".join([
            '    """', indented_doc_str, '    """'
        ])


class CodeGenerator:
    def __init__(self):
        self.type_mapping = {}
        for t in SUPPORTED_TYPES:
            self.type_mapping[t] = t

    def field_type_to_code(self, ift: FieldType, current_class):
        n = self.type_mapping[ift.name]
        if ift.is_parametric:
            cs = ", ".join([self.field_type_to_code(c, current_class) for c in ift.children])
            return f"{n}[{cs}]"
        else:
            if n == current_class:
                return f"'{n}'"
            return f"{n}"

    def field_declaration_to_code(self, item: PydanticFieldDefinition, current_class):
        ts = self.field_type_to_code(item.type, current_class)
        if ts.strip().startswith('typing.Optional'):
            ts = f"{ts} = None"
        return f"{item.name} : {ts}"

    def enum_entry_to_code(self, e: EnumEntry):
        return f"{e.name} = {to_literal(e.value)}"

    def enum_def_to_code(self, item: EnumDefinition):
        tn = self.type_mapping[item.name]
        if item.is_int():
            header = f"class {tn}(IntEnum):"
        else:
            header = f"class {tn}(str, Enum):"
        body = '\n'.join([
            f"    {self.enum_entry_to_code(x)}" for x in item.enum_entries
        ])

        doc_str = doc_to_doc_str(item.doc_str)
        if doc_str is not None:
            return '\n'.join([header, doc_str, body])
        else:
            return '\n'.join([header, body])

    def class_def_to_code(self, item: ClassDefinition):
        tn = self.type_mapping[item.name]
        header = f"class {tn}(BaseModel):"
        body = '\n'.join([
            f"    {self.field_declaration_to_code(x, tn)}" for x in item.fields
        ])
        doc_str = doc_to_doc_str(item.doc_str)
        if doc_str is not None:
            return '\n'.join([header, doc_str, body])
        else:
            return '\n'.join([header, body])

    def class_or_enum_to_code(self, item: Union[ClassDefinition, EnumDefinition]):
        if isinstance(item, ClassDefinition):
            return self.class_def_to_code(item)
        elif isinstance(item, EnumDefinition):
            return self.enum_def_to_code(item)

    def generate_all(self, schema: DatasetSchema):
        # first rename class name if possible
        # generate class one by one based on topo order, which the classes
        # should already have been in that order if it is built by schema builder
        used_names = set()
        for k in self.type_mapping.values():
            used_names.add(k)

        for c in reversed(schema.classes):
            last_name = c.name.split('.')[-1]
            alter_name = last_name

            while alter_name in used_names:
                alter_name = f"{alter_name}_1"

            self.type_mapping[c.name] = alter_name
            used_names.add(alter_name)
        self.type_mapping = self.type_mapping
        header = 'import datetime\n' \
                 'import typing\n' \
                 'from enum import Enum, IntEnum\n' \
                 'import dataset_sh\n' \
                 'from pydantic import BaseModel\n'

        code_body = '\n\n'.join(
            [self.class_or_enum_to_code(c) for c in schema.classes]
        )

        return '\n'.join([
            header, code_body
        ])

    @staticmethod
    def generate_loader_code(store_name, dataset_name, collection_name, entry_class_name):
        entry_class_name = entry_class_name.split('.')[-1]
        code = f"""
with dataset_sh.read('{store_name}/{dataset_name}') as reader:
    for item in reader.coll('{collection_name}', model={entry_class_name}):
        print(item)
        break
"""
        return code

    @staticmethod
    def generate_file_loader_code(filepath, collection_name):
        code = f"""
with dataset_sh.read_file('{filepath}') as reader:
    for item in reader.coll('{collection_name}'):
        print(item)
        break
"""
        return code


def to_literal(v):
    if isinstance(v, str):
        return "'" + v.replace("'", "\\'") + "'"
    elif isinstance(v, int):
        return f"{v}"
