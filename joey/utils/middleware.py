from importlib import import_module


def get_middleware(name):
    module, middleware = name.rsplit('.', maxsplit=1)
    return getattr(import_module(module), middleware)
