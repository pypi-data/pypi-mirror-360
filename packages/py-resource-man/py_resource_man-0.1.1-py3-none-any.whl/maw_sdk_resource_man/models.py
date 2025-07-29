from typing import Optional, List, Union, Literal
from pydantic import BaseModel


class FieldTypeEnum(BaseModel):
    enum: List[str]


class FieldTypeDatetime(BaseModel):
    datetime: dict = {}


FieldType = Union[
    Literal["simple_str", "date", "integer", "float", "double"],
    FieldTypeEnum,
    FieldTypeDatetime,
]


class Field(BaseModel):
    field_name: str
    field_type: FieldType
    field_description: Optional[str] = None


class Manifest(BaseModel):
    description: str
    fields: List[Field]


class Resource(BaseModel):
    __root__: dict  # recurso genérico (sem schema fixo)
