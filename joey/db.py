import re
import typing

import orm
from orm.exceptions import MultipleMatches, NoMatch
from orm.models import ModelMeta


def _find_registry_in_bases(bases):
    for base in bases:
        if registry := getattr(base, "registry", None):
            return registry
    return None


class ModelMetaclass(ModelMeta):
    """
    Add abstract models support to encode/orm

    Abstract models should define `abstract` attribute:

    class Abstract:
        abstract = True
        ...
    """

    def __new__(cls, name, bases, attrs):
        if attrs.get("abstract"):
            # We avoid adding abstract model to model registry
            registry = attrs.pop("registry", _find_registry_in_bases(bases))
            model_class = super().__new__(cls, name, bases, attrs)
            # add registry back to pass it to inherited models
            setattr(model_class, "registry", registry)
        else:
            # collect fields across bases
            fields = {}
            for base in bases:
                fields.update(getattr(base, "fields", {}))
            fields.update(attrs.get("fields", {}))
            attrs["fields"] = fields

            # set registry if it is not explicitly set
            if not attrs.get("registry"):
                attrs["registry"] = _find_registry_in_bases(bases)

            model_class = super().__new__(cls, name, bases, attrs)
        return model_class


class Model(orm.Model, metaclass=ModelMetaclass):
    """
    Base model for joey models

    Purposes:
    - no need to set registry for each model
    - automatic migrations with alembic
    """

    abstract = True
    DoesNotExist = NoMatch
    MultipleObjectsReturned = MultipleMatches


def init(settings):
    import databases

    database = databases.Database(settings.SQLALCHEMY_DATABASE_URI)
    models = orm.ModelRegistry(database=database)

    Model.registry = models
