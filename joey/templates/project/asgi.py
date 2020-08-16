from fastapi import FastAPI

from joey import db
from joey.utils import get_router
from settings import settings


db.init(settings)

app = FastAPI()


for application_name, kwargs in settings.ROUTES:
    app.include_router(get_router(application_name), **kwargs)

