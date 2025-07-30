from datetime import date, datetime, time, timedelta
from enum import IntEnum, Enum
from typing import get_args, get_origin, get_type_hints, Optional

import typing
from pydantic import BaseModel

from .core import EnumEntry, FieldType, PydanticFieldDefinition, EnumDefinition, ClassDefinition, \
    DatasetSchema


def strip_doc(doc_or_none: Optional[str], from_enum=False) -> Optional[str]:
    if doc_or_none is None:
        return None
    else:
        lines = doc_or_none.strip().split('\n')
        doc_str = '\n'.join([l.strip() for l in lines])
        if from_enum and doc_str == 'An enumeration.':
            return None
        return doc_str


class SchemaBuilder:
    def __init__(self):
        self.classes = []
        self.entry_point = ''
        self.visited = set()

    @staticmethod
    def build(model_clz) -> DatasetSchema:
        builder = SchemaBuilder()
        builder.load_main_model(model_clz)
        class_docstring = model_clz.__doc__
        return DatasetSchema(
            entry_point=builder.entry_point,
            classes=builder.classes,
            doc_str=class_docstring
        )

    def load_main_model(self, clz):
        self.entry_point = get_class_full_name(clz)
        self.load_model(clz)

    def load_model(self, clz):
        """
        load a pydantic model definition. (i.e. any class that inherits BaseModel)
        :param clz:
        :return:
        """
        full_name = get_class_full_name(clz)

        if full_name in self.visited:
            return

        self.visited.add(full_name)

        fields = []
        for field_name, field_type in get_type_hints(clz).items():
            t = self.parse_and_load_definition(field_type)
            fields.append(
                PydanticFieldDefinition(name=field_name, type=t)
            )

        c = ClassDefinition(
            name=full_name,
            fields=fields,
            doc_str=strip_doc(clz.__doc__)
        )

        self.classes.append(c)
        return c

    def load_enum(self, clz):
        full_name = get_class_full_name(clz)

        if full_name in self.visited:
            return
        self.visited.add(full_name)

        entries = []
        for name, value in clz.__members__.items():
            entries.append(EnumEntry(name=name, value=value.value))

        c = EnumDefinition(
            name=full_name,
            enum_entries=entries,
            doc_str=strip_doc(clz.__doc__, from_enum=True)
        )
        self.classes.append(c)
        return c

    def parse_and_load_definition(self, clz) -> FieldType:
        if is_pydantic(clz):
            # Load pydantic class
            self.load_model(clz)
            return FieldType.simple(name=get_class_full_name(clz))
        elif is_enum(clz):
            # Load enum def
            self.load_enum(clz)
            return FieldType.simple(name=get_class_full_name(clz))
        else:
            origin = get_origin(clz)
            if origin is not None:
                # Load things like List[xxx], Dict[A,B]
                pt = self.get_parameterized_type(clz, origin)
                if pt is not None:
                    return pt
            else:
                tn = to_primitive_type(clz)
                if tn is not None:
                    return FieldType.simple(name=tn)

        return FieldType.simple(name='typing.Any')

    def get_parameterized_type(self, clz, origin):

        name = None

        if origin is list or origin is typing.List:
            name = 'typing.List'
        elif origin is set or origin is typing.Set:
            name = 'typing.Set'
        elif origin is dict or origin is typing.Dict:
            name = 'typing.Dict'
        elif origin is tuple or origin is typing.Tuple:
            name = 'typing.Tuple'
        elif origin is typing.Union:
            name = 'typing.Union'

        if name is not None:
            args = get_args(clz)
            if name == 'typing.Union':
                if len(args) == 2 and args[-1] is type(None):
                    name = 'typing.Optional'
                    args = [args[0]]

            children = [self.parse_and_load_definition(a) for a in args]
            return FieldType.typed(name=name, children=children)

        # In all other case, we will return none, and let caller handle this.
        return None


def is_pydantic(clz):
    try:
        return issubclass(clz, BaseModel)
    except TypeError:
        return False


def is_enum(clz):
    try:
        return issubclass(clz, Enum) or issubclass(clz, IntEnum)
    except TypeError:
        return False


def to_datetime_types(clz):
    if clz is date:
        return 'datetime.date'
    elif clz is datetime:
        return 'datetime.datetime'
    elif clz is time:
        return 'datetime.time'
    elif clz is timedelta:
        return 'datetime.timedelta'
    return None


def to_primitive_type(clz):
    dt_type = to_datetime_types(clz)
    if dt_type is not None:
        return dt_type

    if clz is int:
        return 'int'
    elif clz is float:
        return 'float'
    elif clz is bool:
        return 'bool'

    elif clz is str:
        return 'str'

    elif clz is list:
        return 'list'

    elif clz is dict:
        return 'dict'

    elif clz is tuple:
        return 'tuple'

    elif clz is set:
        return 'set'

    return None


def get_class_full_name(clz):
    return clz.__module__ + '.' + clz.__name__
