from datetime import datetime as dt

import pytz


def now():
    return dt.utcnow().replace(tzinfo=pytz.utc)
