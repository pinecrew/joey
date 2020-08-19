from pathlib import Path
import subprocess
import argparse
import uuid
import sys

from mako.exceptions import RichTraceback
from mako.template import Template


def render(path, format_render=False, **kwargs):
    text = path.open().read()
    if kwargs and format_render:
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


def is_renderable_template(filepath):
    if filepath.suffix == '.pyt':
        return True, filepath.parent / (filepath.stem + '.py')
    return False, filepath


def register_app(name, config_file):
    route_flag_name = '# joey_route_autoregister_flag'
    app_flag_name = '# joey_app_autoregister_flag'
    application_index, routes_index = None, None
    app_tab, route_tab = '', ''

    to_pretty_route = lambda name, tab: \
        tab + f"'{name}': " + "{'prefix': " + f"'/{name}', 'tags': ['{name}']" + '},\n'
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
    for path in templates_dir.glob('**/*'):
        if '__pycache__' in str(path) or path.is_dir():
            continue

        filepath = app_directory / path.relative_to(templates_dir)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        has_variables, filepath = is_renderable_template(filepath)
        print(f' - {filepath}')
        with filepath.open('w', encoding='utf-8') as f:
            f.write(render(path, has_variables, **variables))

    print('Project `{app_name}` successfully created'.format(**variables))


def app_add(name):
    app_directory = Path(name)
    templates_dir = Path(__file__).parent / 'templates' / 'app'

    print('Start application creation')
    for path in templates_dir.glob('**/*'):
        if '__pycache__' in str(path) or path.is_dir():
            continue

        filepath = app_directory / path.relative_to(templates_dir)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        print(f' - {filepath}')
        with filepath.open('w', encoding='utf-8') as f:
            f.write(render(path))

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
