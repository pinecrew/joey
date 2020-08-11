from pathlib import Path
import argparse


def app_init(name):
    app_directory = Path(name) if name else Path('.')
    print(f'app:init in <{app_directory}> directory')


def app_add(name):
    print(f'app:add application with name <{name}>')


def app_run():
    print('app:run')


def app_revise(label):
    print(f'app:revise with label <{label}>')


def app_migrate():
    print('app:migrate')


def main(argv=None):
    # supported functions
    params = [
        ('init', 'create project skeleton', True, app_init),
        ('add', 'add project application', True, app_add),
        ('run', 'run developer server', False, app_run),
        ('revise', 'create migration', True, app_revise),
        ('migrate', 'apply migration', False, app_migrate)
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
        if hasattr(option, 'argument'):
            option.func(option.argument)
        else:
            option.func()
    else:
        # else print app help
        parser.print_help()