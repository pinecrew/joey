# joey

[![](https://img.shields.io/pypi/v/joey.svg)](https://pypi.org/project/joey/)
[![](https://img.shields.io/pypi/l/joey.svg)](https://github.com/pinecrew/joey/blob/master/LICENSE)

Async web framework on top of [fastapi](https://pypi.org/project/fastapi/) and [orm](https://pypi.org/project/orm/)

# How to start
Let's create demo project
```sh
$ mkdir demo-project
$ cd demo-project
$ pipenv install joey
$ pipenv shell
$ joey init
```

Joey will create the following project structure
```sh
.
├── alembic.ini
├── asgi.py
├── migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions
└── settings
    ├── common.py
    ├── common.yml
    ├── development.py
    └── __init__.py
```

Let's add the application to the given project structure
```sh
$ joey add hello
# or with autoregister parameter
$ joey add -a hello
```

Joey will add the following files in a separate folder
```sh
.
└── hello
    ├── __init__.py
    ├── models.py
    └── routes.py
```

If you use `-a` flag then **joey** automatic register your app and route in project settings file
```yaml
APPLICATIONS:
- hello
ROUTES:
  hello:
    prefix: /hello
    tags:
    - hello
```
otherwise manually edit `settings/common.yml` file.

Now implement model in file  `hello/models.py`
```py
class Item(Model):
    fields = {
        "id": orm.Integer(primary_key=True),
        "text": orm.Text(),
    }
```

Implement a simple route in `hello/routes.py`, than can access to database
```py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


from hello.models import Item


class ItemResponse(BaseModel):
    text: str


router = APIRouter()

@router.get('/{id}', response_model=ItemResponse)
async def item(id: int) -> ItemResponse:
    try:
        return await Item.objects.get(id=id)
    except Item.DoesNotExist:
        raise HTTPException(status_code=404, detail='Item not found')
```


Next step - create a database, then migrate it and add a couple of elements
```sh
$ joey revise 'init database'
$ joey migrate
$ sqlite3 db.sqlite "insert into items (text) values ('hello'), ('joe here');"
```

Everything is ready, now you can start with uvicorn
```sh
$ joey run
# or
$ uvicorn asgi:app --reload
```

And request data with Swagger UI by `http://localhost:8000/docs`.
