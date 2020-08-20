from pathlib import Path
import subprocess
import argparse
import uuid
import yaml
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


def _register_app(name, config_file):
    try:
        config = yaml.load(config_file.open(), Loader=yaml.Loader)
        applications = config['APPLICATIONS']
        routes = config['ROUTES']

        applications.append(name)
        routes[name] = {'prefix': f'/{name}', 'tags': [name]}

        with config_file.open('w') as f:
            yaml.dump(config, f)
        print(f'Autoregister application and route in `{config_file}`')
    except KeyError as e:
        print('Invalid file format: key %s does not exist' % e.args)
    except (TypeError, AttributeError) as e:
        print('Invalid file format')
    except Exception as e:
        print(getattr(e, 'message', repr(e)))


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

    if app_directory.exists():
        print(f'Application folder with name `{name}` already exist')
        return

    templates_dir = Path(__file__).parent / 'templates' / 'app'
    print('Start application creation')
    copy_directory_structure(templates_dir, app_directory, {})

    if autoregister:
        config_file = Path('.') / 'settings' / 'common.yml'
        if config_file.exists():
            _register_app(name, config_file)

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
