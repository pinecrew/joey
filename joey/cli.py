from pathlib import Path
import argparse
import subprocess


def app_init(name=None):
    app_directory = Path(name) if name else Path('.')
    files = {
    'alembic.ini': '''
[alembic]
script_location = migrations
file_template = %%(year)2d%%(month)02d%%(day)02d_%%(hour)02d%%(minute)02d%%(second)02d_%%(rev)s_%%(slug)s

[post_write_hooks]
hooks=black
black.type=console_scripts
black.entrypoint=black
black.options=-l 120 --skip-string-normalization

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
    ''',
    'asgi.py': '''
from importlib import import_module

from fastapi import FastAPI, HTTPException

from joey import db
from settings import settings

db.init(settings)


app = FastAPI()
for application in settings.APPLICATIONS:
    try:
        m = import_module(application + '.routes')
        app.include_router(m.router, prefix='/' + application, tags=[application])
    except:
        pass    
    ''',
    'settings/__init__.py': '''
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator
from typing import List


def variables(module):
    return {k: v for k, v in vars(dev).items() if not k.startswith('_')}


class Settings(BaseSettings):
    PROJECT_NAME: str
    SECRET_KEY: str
    COOKIE_SECRET: str
    SQLALCHEMY_DATABASE_URI: str
    APPLICATIONS: List[str]


try:
    import settings.local as local

    settings = Settings(**variables(local))
except ImportError:
    import settings.development as dev

    settings = Settings(**variables(dev))

    ''',
    'settings/common.py': '''
import typing as _typing

PROJECT_NAME: str = 'JoinTMS'
APPLICATIONS: _typing.List[str] = ['joey.middleware.session', 'items']

    ''',
    'settings/development.py': '''
from .common import *

SECRET_KEY: str = ''
COOKIE_SECRET: str = ''
SQLALCHEMY_DATABASE_URI: str = 'sqlite:///db.sqlite'

    ''',
    'migrations/versions/.empty': '',
    'migrations/env.py': '''
import sys
from importlib import import_module
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config
fileConfig(config.config_file_name)

# add parent dir to python path for proper imports
sys.path += ['.']
from joey.db import Model, init
from settings import settings
init(settings)
target_metadata = Model.__metadata__

# import all models to fill metadata
for app in settings.APPLICATIONS:
    import_module(app + ".models")


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """

    url = settings.SQLALCHEMY_DATABASE_URI
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        {"sqlalchemy.url": settings.SQLALCHEMY_DATABASE_URI}, prefix="sqlalchemy.", poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

    ''',
    'migrations/script.py.mako':'''
"""

Message: ${message}
Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}

    ''',
    }
    for filename, contents in files.items():
        filepath = app_directory / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open("w", encoding ="utf-8") as f:
            f.write(contents)


def app_add(name):
    app_directory = Path(name)
    files = {
    '__init__.py': '',
    'models.py': '''
import orm

from joey.db import Model
    ''',
    'routes.py':'''
from fastapi import APIRouter, HTTPException

router = APIRouter()
''',
    }
    for filename, contents in files.items():
        filepath = app_directory / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open("w", encoding ="utf-8") as f:
            f.write(contents)


def app_run():
    subprocess.call(['uvicorn', '--reload', 'asgi:app'])


def app_revise(label='auto'):
    subprocess.call(['alembic', 'revision', '-m', label, '--autogenerate'])


def app_migrate():
    subprocess.call(['alembic', 'upgrade', 'head'])


def main(argv=None):
    # supported functions
    params = [
        ('init', 'create project skeleton', True, app_init),
        ('add', 'add project application', True, app_add),
        ('run', 'run developer server', False, app_run),
        ('revise', 'create migration', True, app_revise),
        ('migrate', 'apply migration', False, app_migrate),
    ]

    parser = argparse.ArgumentParser(description='Async web framework on top of fastapi and orm')

    # create subparsers
    subparser = parser.add_subparsers()
    for name, help_info, has_args, function in params:
        s_parse = subparser.add_parser(name, help=help_info)
        if has_args:
            s_parse.add_argument(dest='argument', nargs='?', type=str, default='', help='command parameter')
        s_parse.set_defaults(func=function)

    option = parser.parse_args(argv)
    # if args has func, then execute this function
    if hasattr(option, 'func'):
        # with arguments?
        if hasattr(option, 'argument') and option.argument:
            option.func(option.argument)
        else:
            option.func()
    else:
        # else print app help
        parser.print_help()
