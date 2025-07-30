from typing import Union, Optional, List

import easytype.core as etc
from pydantic import BaseModel


class EnumEntry(BaseModel):
    name: str
    value: str


class FieldType(BaseModel):
    is_parametric: bool
    name: str
    children: Optional[List['FieldType']] = None

    @staticmethod
    def simple(name):
        return FieldType(is_parametric=False, name=name)

    @staticmethod
    def typed(name, children):
        return FieldType(is_parametric=True, name=name, children=children)

    def to_new_type_system(self) -> Union[etc.PrimitiveType, etc.ParameterizedType, str]:
        if self.is_parametric:
            params = [c.to_new_type_system() for c in self.name]
            ret = etc.ParameterizedType(name=self.name, params=params)
            return ret
        else:
            ret = etc.PrimitiveType
            return ret

    def get_types_to_build(self) -> List[str]:
        pass


class PydanticFieldDefinition(BaseModel):
    name: str
    type: FieldType

    def to_new_type_system(self) -> etc.FieldDefinition:
        ret = etc.FieldDefinition(
            name=self.name,
            type=self.type.to_new_type_system(),
            comment=None,
        )
        return ret

    def get_types_to_build(self) -> List[str]:
        pass


class EnumDefinition(BaseModel):
    name: str
    enum_entries: Optional[List[EnumEntry]]
    doc_str: Optional[str] = None

    def is_int(self):
        if self.enum_entries is not None and len(self.enum_entries) > 0:
            return isinstance(self.enum_entries[0].value, int)
        return False

    def to_new_type_system(self) -> etc.EnumType:
        ret = etc.EnumType(
            name=self.name,
            choices=[x.value for x in self.enum_entries],
            comment=self.doc_str
        )
        return ret

    def get_types_to_build(self) -> List[str]:
        pass


class ClassDefinition(BaseModel):
    name: str
    fields: List[PydanticFieldDefinition]
    doc_str: Optional[str] = None

    def to_new_type_system(self) -> etc.UserDefinedType:
        return etc.UserDefinedType(
            name=self.name,
            fields=[x.to_new_type_system() for x in self.fields],
            comment=self.doc_str
        )

    def get_types_to_build(self) -> List[str]:
        pass


class DatasetSchema(BaseModel):
    entry_point: str
    classes: List[Union[EnumDefinition, ClassDefinition]]

    def to_new_type_system(self) -> etc.UserDefinedType:
        def_lookup = {}
        build_order = self._get_build_order()
        for c in self.classes:
            def_lookup[c.name] = c.to_new_type_system()
        etc.UserDefinedType(name='', comment='')
