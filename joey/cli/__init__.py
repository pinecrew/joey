from pathlib import Path
import subprocess
import click
import uuid
import sys

from .utils import copy_directory_structure, register_app


@click.group()
def cli():
    '''Async web framework on top of fastapi and orm'''
    pass


@cli.command()
@click.argument('name', required=False)
def init(name=None):
    '''Create project skeleton'''
    app_directory = Path(name) if name else Path('.')
    variables = {
        'app_name': name if name else app_directory.cwd().name,
        'secret_key': uuid.uuid4().hex,
        'cookie_secret': uuid.uuid4().hex,
    }
    templates_dir = Path(__file__).parent / 'templates' / 'project'

    print('Start project creation')
    copy_directory_structure(templates_dir, app_directory, variables)
    print('Project `{app_name}` successfully created'.format(**variables))


@cli.command()
@click.argument('name')
@click.option('--autoregister', '-a', is_flag=True, default=False, help='Autoregister application')
def add(name, autoregister):
    '''Add application to current project'''
    app_directory = Path(name)

    if app_directory.exists():
        print(f'Application folder with name `{name}` already exist')
        return

    templates_dir = Path(__file__).parent / 'templates' / 'app'
    print('Start application creation')
    copy_directory_structure(templates_dir, app_directory, {})

    if autoregister:
        config_file = Path('.') / 'settings' / 'common.yml'
        if config_file.exists():
            register_app(name, config_file)

    print(f'Application `{name}` successfully added')


@cli.command()
def run():
    '''Run developer server'''
    try:
        subprocess.call(['uvicorn', '--reload', 'asgi:app'])
    except FileNotFoundError:
        print('Uvicorn is not installed. Run asgi:app with your favorite async server.')
    except KeyboardInterrupt:
        pass


@cli.command()
@click.argument('label', required=False)
def revise(label='auto'):
    '''Create migration'''
    subprocess.call(['alembic', 'revision', '-m', label, '--autogenerate'])


@cli.command()
def migrate():
    '''Apply migration'''
    subprocess.call(['alembic', 'upgrade', 'head'])


def main(argv=None):
    cli(args=argv)
