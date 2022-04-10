import re
import typing

import orm
from orm.models import ModelMeta
from orm.exceptions import MultipleMatches, NoMatch


class ModelMetaclass(ModelMeta):
    def __new__(cls, name, bases, attrs):
        model_class = type.__new__(cls, name, bases, attrs)

        if attrs.get("abstract"):
            return model_class

        if model_class.registry:
            model_class.database = model_class.registry.database
            model_class.registry.models[name] = model_class

            if "tablename" not in attrs:
                setattr(model_class, "tablename", name.lower())

        for name, field in model_class.fields.items():
            setattr(field, "registry", model_class.registry)
            if field.primary_key:
                model_class.pkname = name

        model_class.build_table()

        return model_class


class Model(orm.Model, metaclass=ModelMetaclass):
    abstract = True
    DoesNotExist = NoMatch
    MultipleObjectsReturned = MultipleMatches


class DB:
    def __init__(self, settings):
        import databases

        self.database = databases.Database(settings.SQLALCHEMY_DATABASE_URI)
        self.models = orm.ModelRegistry(database=self.database)

        Model.registry = self.models

def init(settings):
    return DB(settings)
