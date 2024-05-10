# Example Package

This is a simple example package. You can use
[Репозиторий GitHub](https://github.com/DephPhascow/py-graphql)
to write your content

## Отправка файла

```python
from py_simple_graphql.utils import gen_send_file

def file_upload():
  return gen_send_file(
    name="fileUpload",
    var={
      "img": "Upload!",
      "name": "String!"
    }
  )
```

И затем сам запуск:

```python
import asyncio
from tests.mutations import file_upload
from tests.settings import gql

async def main():
    executor = gql.add_query("send_file", file_upload())
    res = await executor.execute(variables={
        "img": "tests/1.jpeg",
        "name": "Py-Simple-GraphQL"
    })
    print(res)

asyncio.run(main())
```

На сервер придет ответ:

```python
img = {
    'file': <_io.BytesIO object at 0x7f44efdba9f0>, 
    '_name': '1.jpeg', 
    'size': 36164,
    'content_type': '', 
    'charset': None,
    'content_type_extra': {},
    'field_name': 'img'
}
name: "Py-Simple-Graphql"
```
