import logging
import subprocess
import sys
import uuid
from pathlib import Path
from functools import wraps

import click

from .utils import copy_directory_structure, register_app

logger = logging.getLogger('cli')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def verbose(func):
    @wraps(func)
    def wrapper(verbose, *args, **kwargs):
        if verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        return func(*args, **kwargs)

    return click.option('--verbose', '-v', is_flag=True, default=False, help='Verbose output')(wrapper)


@click.group()
@verbose
def cli():
    '''Async web framework on top of fastapi and orm'''
    pass


@cli.command()
@click.argument('name', required=False)
@verbose
def init(name=None):
    '''Create project skeleton'''
    app_directory = Path(name) if name else Path('.')
    variables = {
        'app_name': name if name else app_directory.cwd().name,
        'secret_key': uuid.uuid4().hex,
        'cookie_secret': uuid.uuid4().hex,
    }
    templates_dir = Path(__file__).parent / 'templates' / 'project'

    logger.debug('Start project creation')
    copy_directory_structure(templates_dir, app_directory, variables)
    logger.info('Project `{app_name}` successfully created'.format(**variables))


@cli.command()
@click.argument('name')
@click.option('--autoregister', '-a', is_flag=True, default=False, help='Autoregister application')
@verbose
def add(name, autoregister):
    '''Add application to current project'''
    app_directory = Path(name)

    if app_directory.exists():
        logger.error(f'Application folder with name `{name}` already exist')
        return

    templates_dir = Path(__file__).parent / 'templates' / 'app'
    logger.debug('Start application creation')
    copy_directory_structure(templates_dir, app_directory, {})

    if autoregister:
        config_file = Path('.') / 'settings' / 'common.yml'
        if config_file.exists():
            register_app(name, config_file)

    logger.info(f'Application `{name}` successfully added')


@cli.command()
@verbose
def run():
    '''Run developer server'''
    try:
        subprocess.call(['uvicorn', '--reload', 'asgi:app'])
    except FileNotFoundError:
        logger.error('Uvicorn is not installed. Run asgi:app with your favorite async server.')
    except KeyboardInterrupt:
        pass


@cli.command()
@click.argument('label', required=False)
@verbose
def revise(label='auto'):
    '''Create migration'''
    subprocess.call(['alembic', 'revision', '-m', label, '--autogenerate'])


@cli.command()
@verbose
def migrate():
    '''Apply migration'''
    subprocess.call(['alembic', 'upgrade', 'head'])


def main(argv=None):
    cli(args=argv)
