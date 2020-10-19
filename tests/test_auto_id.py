import asyncio
import functools

import pytest
import orm
import databases
import sqlalchemy

import tests.settings as settings

from joey import db

db_context = db.init(settings)

@pytest.fixture(autouse=True, scope="module")
def create_test_database():
    engine = db_context.engine
    metadata = db_context.metadata
    metadata.create_all(engine)
    yield
    metadata.drop_all(engine)

class Example(db.Model):
    description = orm.Text(allow_blank=True)

def async_adapter(wrapped_func):
    """
    Decorator used to run async test cases.
    """

    @functools.wraps(wrapped_func)
    def run_sync(*args, **kwargs):
        loop = asyncio.get_event_loop()
        task = wrapped_func(*args, **kwargs)
        return loop.run_until_complete(task)

    return run_sync


@async_adapter
async def test_auti_id():
    await Example.objects.create()

    example = await Example.objects.get()
    assert example.id == 1
    assert example.description == ''
