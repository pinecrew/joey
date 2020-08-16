# joey

[![](https://img.shields.io/pypi/v/joey.svg)](https://pypi.org/project/joey/)
[![](https://img.shields.io/pypi/l/joey.svg)](https://github.com/pinecrew/joey/blob/master/LICENSE)

Async web framework on top of fastapi and orm

# How to start
Let's create demo project
```sh
$ joey init demo-project
# or create in current folder
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
    ├── development.py
    └── __init__.py
```

Let's add the application to the given project structure
```sh
$ joey add hello
```

Joey will add the following files in a separate folder
```sh
.
└── hello
    ├── __init__.py
    ├── models.py
    └── routes.py
```

Now you can register a new application in the project settings (`settings/common.py`)
```py
APPLICATIONS: _typing.List[str] = ['hello']
ROUTES: _typing.Dict[str, dict] = {
    'hello': {'prefix': '/hello', 'tags': ['hello_tags']}
}
```

Now implement model in file  `hello/models.py`
```py
class Item(Model):
    id = orm.Integer(primary_key=True)
    text = orm.Text()
```

Implement a simple route in `hello/routes.py`, than can access to database
```py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


from hello.models import Item as ItemDB


class Item(BaseModel):
    text: str


router = APIRouter()

@router.post('/{id}', response_model=Item)
async def item(id: int) -> Item:
    try:
        return await ItemDB.objects.get(id=id)
    except ItemDB.DoesNotExist:
        raise HTTPException(status_code=404, detail='Item not found')
```


Next step -- create a database, then migrate it and add a couple of elements
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