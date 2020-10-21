from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass
from pydantic.utils import GetterDict
from typing import List, Optional, Any


class NestedGetterDict(GetterDict):
    def get(self, key: Any, default: Any = None):
        res = self._obj
        for s in key.split('.'):
            res = getattr(res, s, default)
        return res


class SerializerMetaclass(ModelMetaclass):
    def __call__(cls, obj=None, **kwargs):
        if obj is None:
            return super(SerializerMetaclass, cls).__call__(**kwargs)
        if isinstance(obj, dict):
            return cls.parse_obj(obj)
        return cls.from_orm(obj)


class Serializer(BaseModel, metaclass=ModelMetaclass):
    class Config:
        orm_mode = True
        getter_dict = NestedGetterDict
