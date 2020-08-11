from pathlib import Path
import argparse


def app_init():
    print('app:init')


def app_add(args):
    print(f'app:add {args}')


def app_run():
    print('app:run')


def app_revise(args):
    print(f'app:revise {args}')


def app_migrate():
    print('app:migrate')


if __name__ == '__main__':
    # supported functions
    params = [
        ('init', 'create project skeleton', False, app_init),
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
            s_parse.add_argument(dest='args', type=str, default='')
        s_parse.set_defaults(func=function)

    option = parser.parse_args()
    # if args has func, then execute this function
    if hasattr(option, 'func'):
        if hasattr(option, 'args'):
            option.func(option.args)
        else:
            option.func()
    else:
        # else print app help
        parser.print_help()