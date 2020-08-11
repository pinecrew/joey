from uuid import uuid4

import orm

from utils import timezone
from db import Model


class Session(Model):
    uuid = orm.String(default=lambda: uuid4().hex, primary_key=True, max_length=32)
    data = orm.JSON(default=dict)
    expiration_date = orm.DateTime()
