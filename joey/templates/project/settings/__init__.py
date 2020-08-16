from typing import List, Dict

from pydantic import BaseSettings


def variables(module):
    return {k: v for k, v in vars(dev).items() if not k.startswith('_')}


class Settings(BaseSettings):
    PROJECT_NAME: str
    SECRET_KEY: str
    COOKIE_SECRET: str
    SQLALCHEMY_DATABASE_URI: str
    APPLICATIONS: List[str]
    ROUTES: Dict[str, dict]


try:
    import settings.local as local

    settings = Settings(**variables(local))
except ImportError:
    import settings.development as dev

    settings = Settings(**variables(dev))