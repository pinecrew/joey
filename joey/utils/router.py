from importlib import import_module


def get_router(application_name):
    return import_module(application_name + '.routes').router
