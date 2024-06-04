# Py-Simple-GraphQL

[Репозиторий GitHub](https://github.com/DephPhascow/py-graphql)

В проекте используется [JmesPath](https://jmespath.org/)

## Настройки

```python
# settings.py
from py_simple_graphql.graphql import GraphQL, GraphQLConfig

gql = GraphQL(
    gql_config=GraphQLConfig(
        http=GRAPHQL_URL, # Ссылка на graphql
        ws=WS_URL, # Ссылка на graphql ws
        DEBUG=True, # Включить ли логирование (Есть 2 типа)
    )
)

# Логгер есть 2 типа:
# 1) FileLogger(file_name="log.txt") - Все данные сохраняет в файл
# 2) ConsoleLogger() - Вывводит всё в консоль

async def init(gql: GraphQL):
    gql.set_logger(FileLogger(file_name="log.txt"))
    
asyncio.run(init(gql))
```

После этого, создаем queres

```python
#queres.py
from py_simple_graphql.utils import gen_query

def users():
  return gen_query(
    name="users", # Имя query запроса
    request="tgId", # поля что запрашиваем
    q_words="data.users[:].tgId" # Синтаксис JMesPath, для преобразования
  )
```

Оно сгенерирует следующий запрос:

```graphql
  users {
    tgId
  }
```

И наконец, выполняем запрос

```python
from tests.settings import gql
from tests.queres import users

executor = gql.add_query("ИмяЗапроса", users())
res = await executor.execute()
print(res)
# ReturnedTypes(values={'users': ['123', '456', '789']})
users = res['users']
print(res)
# ['123', '456', '789']
```

Сам запрос автоматически сгенерирует правельный GraphQL синтаксис

```graphql
query {
  users {
    tgId
  }
}
```

Допустим, у нас есть еще 1 запрос.

```python
#queres.py
from py_simple_graphql.utils import gen_query

def directionals():
  return gen_query(
    name="directionals",
    request="name", 
    q_words="data.directionals[:].name",
    var={
      "filters": "DirectionModelFilter"
    }
  )
```

```python
from tests.settings import gql
from tests.queres import users, directionals

executor = gql.add_query("QueryName", users())
executor.add_query(directionals())
res = await executor.execute(variables: {
  "filters": {
    "name":  {
      "contains": "Te"
    }    
  }
})
print(res)
# ReturnedTypes(values={'users': ['Terry', ]})
```

Это автоматически сгенерирует запрос:

```graphql
query ($filters: DirectionModelFilter) {
  users {
    tgId
  }
  directionals (filters: $filters) {
    name
  }
}
```

## Коротко о q_words в классе Query

Если мы пошлем запрос в виде:

```graphql
query {
  users {
    name
    type {
      name
    }
  }
}
```

То мы получим результат:

```python
result = [
  {
    "data": {
      "users": [
        {
          "name": "Deph",
          "type": {
            "name": "Admin"
          }
        }
      ]
    }
  }
]
```

Но это выглядит не красиво и грамоздно, посему если Вы не используете q_words, то оно автоматически подставит `q_words = 'data.queryName'` тем самым Вы получите только:

```python
result = [
  {
    "name": "Deph",
    "type": {
      "name": "Admin"
    }
  }
]
```

Однако, если знать синтаксис jmespath то можно написать: `q_words = 'data.user[:]{name: name, type: type.name}'`

То по итогу получим

```python
result = [
  {
    "name": "Deph",
    "type": "Admin"
  }
]
```

Кроме того, Вы можете создать тип:

```python
from py_simple_graphql.gql_type import GQLType
from dataclasses import dataclass

@dataclass
class UserType(GQLType):
    name: str
    type: str
```

И в Query указать:

```python
from py_simple_graphql.utils import gen_query

def users():
  return gen_query(
    name="directionals",
    request="name, type { name } ",
    to_type=UserType,
    q_words="data.users[:].{name: name, type: type.name}"
  )
```

То в итоге мы получим массив UserType.

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
