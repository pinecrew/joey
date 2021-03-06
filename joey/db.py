import re
import typing

import orm
from orm.models import ModelMetaclass
from orm.exceptions import MultipleMatches, NoMatch


re_camel_case = re.compile(r'(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))')


def capital_case_to_snake_case(value: str) -> str:
    return re_camel_case.sub(r'_\1', value).strip('_').lower()


def find_attr(attr: str, bases: typing.Sequence[type]) -> typing.Optional[typing.Any]:
    for base in bases:
        if hasattr(base, attr):
            return getattr(base, attr)
    return None


class BaseMetaclass(ModelMetaclass):
    def __new__(cls: type, name: str, bases: typing.Sequence[type], attrs: dict) -> type:

        for attr in ['__metadata__', '__database__']:
            if attr not in attrs:
                attrs[attr] = find_attr(attr, bases)

        if '__tablename__' not in attrs:
            attrs['__tablename__'] = capital_case_to_snake_case(name) + 's'

        new_model = super(BaseMetaclass, cls).__new__(  # type: ignore
            cls, name, bases, attrs
        )

        return new_model


class Model(orm.Model, metaclass=BaseMetaclass):
    __abstract__ = True

    id = orm.Integer(primary_key=True)

    DoesNotExist = NoMatch
    MultipleObjectsReturned = MultipleMatches


class DB:
    def __init__(self, settings):
        import databases
        import sqlalchemy

        self.database = databases.Database(settings.SQLALCHEMY_DATABASE_URI)
        self.metadata = sqlalchemy.MetaData()
        self.engine = sqlalchemy.create_engine(str(self.database.url))

        Model.__metadata__ = self.metadata
        Model.__database__ = self.database

def init(settings):
    return DB(settings)
