from importlib import import_module

from fastapi import FastAPI

from joey import db
from settings import settings


db.init(settings)

app = FastAPI()


def router(application_name):
    return import_module(application_name + '.routes').router


for application_name, kwargs in settings.ROUTES:
    app.include_router(router(application_name), **kwargs)

