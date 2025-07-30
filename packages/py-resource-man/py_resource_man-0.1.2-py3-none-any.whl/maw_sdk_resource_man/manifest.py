from typing import Union, List, get_type_hints
from pydantic import BaseModel
from .types import *

class FieldModel(BaseModel):
    field_name: str
    field_type: Union[str, dict]
    field_description: str = ""

class ManifestModel(BaseModel):
    description: str
    fields: List[FieldModel]

def build_manifest(cls) -> ManifestModel:
    hints = get_type_hints(cls)
    fields = []
    for name, typ in hints.items():
        field = getattr(cls, name, typ)
        if isinstance(field, Enum):
            fields.append(FieldModel(field_name=name, field_type={"enum": field.choices}))
        elif typ == SimpleStr:
            fields.append(FieldModel(field_name=name, field_type="simple_str"))
        elif typ == Integer:
            fields.append(FieldModel(field_name=name, field_type="integer"))
        elif typ == Float:
            fields.append(FieldModel(field_name=name, field_type="float"))
        elif typ == Double:
            fields.append(FieldModel(field_name=name, field_type="double"))
        elif typ == Date:
            fields.append(FieldModel(field_name=name, field_type="date"))
        elif typ == Datetime:
            fields.append(FieldModel(field_name=name, field_type={"datetime": {}}))
        else:
            raise TypeError(f"Unsupported type: {typ}")
    return ManifestModel(description=f"{cls.__name__} manifest", fields=fields)
