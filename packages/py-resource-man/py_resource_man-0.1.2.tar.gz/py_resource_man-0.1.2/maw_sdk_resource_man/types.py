from datetime import date, datetime
from typing import Optional

class SimpleStr(str): pass
class Integer(int): pass
class Float(float): pass
class Double(float): pass
class Date(date): pass
class Datetime(datetime): pass

class Enum(str):
    def __new__(cls, *_, values: list[str], desc: Optional[str] = None):
        obj = str.__new__(cls, "enum")
        obj.choices = values
        obj.desc = desc
        return obj
