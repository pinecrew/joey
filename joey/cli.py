from pathlib import Path
import subprocess
import argparse
import uuid


def from_file(filename, **kwargs):
    joey_wd = Path(__file__).parent
    text = (joey_wd / filename).open().read()
    if len(kwargs) > 0:
        return text.format(**kwargs)
    return text


def app_init(name=None):
    app_directory = Path(name) if name else Path('.')
    app_name = name if name else app_directory.cwd().name
    files = {
        'alembic.ini': from_file('templates/alembic.template'),
        'asgi.py': from_file('templates/asgi.template'),
        'settings/__init__.py': from_file('templates/settings_init.template'),
        'settings/common.py': from_file('templates/settings_common.template', app_name=app_name),
        'settings/development.py': from_file(
            'templates/settings_development.template', secret_key=uuid.uuid4().hex, cookie_secret=uuid.uuid4().hex
        ),
        'migrations/versions/.empty': '',
        'migrations/env.py': from_file('templates/migrations_env.template'),
        'migrations/script.py.mako': from_file('templates/migrations_script.template'),
    }
    for filename, contents in files.items():
        filepath = app_directory / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open('w', encoding='utf-8') as f:
            f.write(contents)
    print(f'[info] create project with name {app_name}')


def app_add(name):
    app_directory = Path(name)
    files = {
        '__init__.py': '',
        'models.py': from_file('templates/app.template'),
        'routes.py': from_file('templates/routes.template'),
    }
    for filename, contents in files.items():
        filepath = app_directory / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open('w', encoding='utf-8') as f:
            f.write(contents)
    print(f'[info] add application {name}')


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
