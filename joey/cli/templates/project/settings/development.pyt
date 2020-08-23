from .common import *

# TODO: change secret key
SECRET_KEY: str = '${secret_key}'
# TODO: change cookie secret
COOKIE_SECRET: str = '${cookie_secret}'
# TODO: change database uri
SQLALCHEMY_DATABASE_URI: str = 'sqlite:///db.sqlite'