from importlib import import_module

from fastapi import FastAPI

from joey import db
from settings import settings

db.init(settings)


app = FastAPI()
for application in settings.APPLICATIONS:
    try:
        m = import_module(application + '.routes')
        app.include_router(m.router, prefix='/' + application, tags=[application])
    except:
        pass
