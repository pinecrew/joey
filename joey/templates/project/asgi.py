from importlib import import_module

from fastapi import FastAPI

from joey import db
from settings import settings


db.init(settings)


app = FastAPI()


def router(module_name):
    return import_module(module_name).router


# Specify routers below

# for example:
# app.include_router(router('application.routes'), prefix='/application' , tags=['application'])
