from fastapi import FastAPI
from joey import db, utils


class Application(FastAPI):
    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db.init(settings)
        for application_name, properties in settings.ROUTES.items():
            self.include_router(utils.get_router(application_name), **properties)
        for middleware_name, properties in settings.MIDDLEWARE.items():
            self.add_middleware(utils.get_middleware(middleware_name), **properties)
