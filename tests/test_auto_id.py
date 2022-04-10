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
    async_adapter(db_context.models.create_all)()
    yield
    async_adapter(db_context.models.drop_all)()


def async_adapter(wrapped_func):
    """
    Decorator used to run async test cases.
    """

    @functools.wraps(wrapped_func)
    def run_sync(*args, **kwargs):
        task = wrapped_func(*args, **kwargs)
        return asyncio.run(task)

    return run_sync

class Example(db.Model):
    fields = {
        "id": orm.Integer(primary_key=True),
        "description": orm.Text(allow_blank=True),
    }

@async_adapter
async def test_example():
    await Example.objects.create()

    example = await Example.objects.get()
    assert example.id == 1
    assert example.description == ''

class Parent(db.Model):
    abstract = True
    fields = {
        "id": orm.Integer(primary_key=True),
    }

class Child(Parent):
    fields = {
        "description": orm.Text(allow_blank=True),
    }

@async_adapter
async def test_abstract():
    await Child.objects.create()

    example = await Child.objects.get()
    assert example.id == 1
    assert example.description == ''