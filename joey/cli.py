from pathlib import Path
import subprocess
import argparse
import uuid


def render(path, **kwargs):
    text = path.open().read()
    if kwargs:
        try:
            return text.format(**kwargs)
        except:
            pass
    return text


def app_init(name=None):
    app_directory = Path(name) if name else Path('.')
    variables = {
        'app_name': name if name else app_directory.cwd().name,
        'secret_key': uuid.uuid4().hex,
        'cookie_secret': uuid.uuid4().hex,
    }
    templates_dir = Path(__file__).parent / 'templates' / 'project'
    for path in templates_dir.glob('**/*'):
        if '__pycache__' in str(path) or path.is_dir():
            continue
        filepath = app_directory / path.relative_to(templates_dir)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        print(filepath)
        with filepath.open('w', encoding='utf-8') as f:
            f.write(render(path, **variables))
    print('Create project {app_name}'.format(**variables))


def app_add(name):
    app_directory = Path(name)
    templates_dir = Path(__file__).parent / 'templates' / 'app'
    for path in templates_dir.glob('**/*'):
        if '__pycache__' in str(path) or path.is_dir():
            continue
        filepath = app_directory / path.relative_to(templates_dir)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open('w', encoding='utf-8') as f:
            f.write(render(path))
    print(f'Add application {name}')


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
