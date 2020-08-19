from pathlib import Path
import subprocess
import argparse
import uuid
import sys

from mako.exceptions import RichTraceback
from mako.template import Template


def render(text, **kwargs):
    if kwargs:
        try:
            template = Template(text)
            return template.render(**kwargs)
        except:
            traceback = RichTraceback()
            print(f'[error]: template rendering error at file `{path.name}`')
            for (filename, lineno, function, line) in traceback.traceback:
                print(f'  file {filename}, line {lineno}, in {function}\n    {line}')
            print(f'  {str(traceback.error.__class__.__name__)}: {traceback.error}')
            exit(-1)
    return text


def _is_renderable_template(path):
    return path.suffix == '.pyt'


def _redered_path(template_path):
    return template_path.with_suffix('.py')


def copy_directory_structure(src, dst, context):
    for path in src.glob('**/*'):
        if path.is_dir() or path.suffix == '.pyc':
            continue

        text = path.open().read()
        if _is_renderable_template(path):
            text = render(text, **context)
            path = _redered_path(path)

        filepath = dst / path.relative_to(src)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        print(f' - {filepath}')
        with filepath.open('w') as f:
            f.write(text)


def register_app(name, config_file):
    route_flag_name = '# joey_route_autoregister_flag'
    app_flag_name = '# joey_app_autoregister_flag'
    application_index, routes_index = None, None
    app_tab, route_tab = '', ''

    to_pretty_route = lambda name, tab: tab + f"'{name}': " + "{'prefix': " + f"'/{name}', 'tags': ['{name}']" + '},\n'
    to_pretty_app = lambda name, tab: f"{tab}'{name}',\n"
    generate_tabs = lambda tab_size: ' ' * tab_size if tab_size > 0 else ' ' * 4

    config_data = config_file.open().readlines()

    for index, line in enumerate(config_data):
        if app_flag_name in line and not application_index:
            application_index = index
            app_tab = generate_tabs(line.find(app_flag_name))
        if route_flag_name in line and not routes_index:
            routes_index = index
            route_tab = generate_tabs(line.find(route_flag_name))

    if application_index and routes_index:
        route_text = to_pretty_route(name, route_tab)
        app_text = to_pretty_app(name, app_tab)
        if application_index < routes_index:
            config_data.insert(application_index, app_text)
            config_data.insert(routes_index + 1, route_text)
        else:
            config_data.insert(routes_index, route_text)
            config_data.insert(application_index + 1, app_text)

        with config_file.open('w') as f:
            result = ''.join(config_data)
            f.write(result)

        print(f'Autoregister application and route in `{config_file}`')


def app_init(name=None):
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


def app_add(name, autoregister=False):
    app_directory = Path(name)
    templates_dir = Path(__file__).parent / 'templates' / 'app'

    print('Start application creation')
    copy_directory_structure(templates_dir, app_directory, {})

    if autoregister:
        config_file = Path('.') / 'settings' / 'common.py'
        if config_file.exists():
            register_app(name, config_file)

    print(f'Application `{name}` successfully added')


def app_run():
    try:
        subprocess.call(['uvicorn', '--reload', 'asgi:app'])
    except FileNotFoundError:
        print('Uvicorn is not installed. Run asgi:app with your favorite async server.')
    except KeyboardInterrupt:
        pass


def app_revise(label='auto'):
    subprocess.call(['alembic', 'revision', '-m', label, '--autogenerate'])


def app_migrate():
    subprocess.call(['alembic', 'upgrade', 'head'])


def main(argv=None):
    parser = argparse.ArgumentParser(description='Async web framework on top of fastapi and orm')
    subparser = parser.add_subparsers()

    p_init = subparser.add_parser('init', help='create project skeleton')
    p_init.add_argument(dest='name', type=str, help='project name')
    p_init.set_defaults(func=app_init)

    p_add = subparser.add_parser('add', help='add project application')
    p_add.add_argument('-a', dest='autoregister', action='store_true', default=False, help='autoregister application')
    p_add.add_argument(dest='name', type=str, help='application name')
    p_add.set_defaults(func=app_add)

    p_run = subparser.add_parser('run', help='run developer server')
    p_run.set_defaults(func=app_run)

    p_revise = subparser.add_parser('revise', help='create migration')
    p_revise.add_argument(dest='label', type=str, help='migration label')
    p_revise.set_defaults(func=app_revise)

    p_migrate = subparser.add_parser('migrate', help='apply migration')
    p_migrate.set_defaults(func=app_migrate)

    option = parser.parse_args(argv)
    if hasattr(option, 'func'):
        # TODO: rewrite this shitcode
        function = option.func
        option.__dict__.pop('func')
        function(**option.__dict__)
    else:
        parser.print_help()
