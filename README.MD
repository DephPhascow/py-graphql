# Example Package

This is a simple example package. You can use
[Репозиторий GitHub](https://github.com/DephPhascow/py-graphql)
to write your content

В проекте используется [JmesPath](https://jmespath.org/)

## Оглавление

* [Настройки](#settings)
* [Отправить файл](#send-file)

## <a href="#settings">Настройка</a>

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

Допустим, нас есть еще 1 запрос.

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

executor = gql.add_query("ИмяЗапроса", users())
executor.add_query(directionals())
res = await executor.execute(variables: {
  "filters": {
    "name":  {
      "contains": "те"
    }    
  }
})
print(res)
# ['123', '456', '789']
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

## <a href="#send-file"></a> #Отправка файла

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
