from pathlib import Path

import yaml
from mako.exceptions import RichTraceback
from mako.template import Template


def _render(text: str, **kwargs) -> str:
    if kwargs:
        try:
            template = Template(text)
            return template.render(**kwargs)
        except:
            traceback = RichTraceback()
            print(f'[error]: template rendering error')
            for (filename, lineno, function, line) in traceback.traceback:
                print(f'  file {filename}, line {lineno}, in {function}\n    {line}')
            print(f'  {str(traceback.error.__class__.__name__)}: {traceback.error}')
            exit(-1)
    return text


def _is_renderable_template(path: Path) -> bool:
    return path.suffix == '.pyt'


def _redered_path(template_path: Path) -> Path:
    return template_path.with_suffix('.py')


def copy_directory_structure(src: Path, dst: Path, context: dict):
    for path in src.glob('**/*'):
        if path.is_dir() or path.suffix == '.pyc':
            continue

        text = path.open().read()
        if _is_renderable_template(path):
            text = _render(text, **context)
            path = _redered_path(path)

        filepath = dst / path.relative_to(src)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        print(f' - {filepath}')
        with filepath.open('w') as f:
            f.write(text)


def register_app(name: str, config_file: Path):
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
