from graphql.core.auth import Auth
from .core.utils import gen_mutate, gen_fragment
from .settings import gql

def gen_operation_info():
  return gen_fragment(
    name="operationInfo",
    type_name="OperationInfo",
    request="""
      messages {
        kind
        message
        field
        code
      }
    """
  )

def get_or_create_password():
  return gen_mutate(
    name="getOrCreatePassword",
    var={
      "$tgId": "String!",
      "$firstName": "String!",
      "$lastName": "String",
      "$username": "String",
      "$isPatient": "Boolean!",
    }
  )

def update_user_data():
  return gen_mutate(
    name="updateUser",
    request="...operationInfo",
    var={
      "$data": "UserModelPartial!",
    }
  )
  

async def run_get_or_create_password(tg_id: str, first_name: str, last_name: str, username: str, is_patient: bool):
  # auth = Auth(123, "123", gql)
  # gql.set_auth(auth)
  executor = gql.add_query("get_or_create_password", get_or_create_password())
  return await executor.execute({
    "tgId": f'{tg_id}',
    "firstName": first_name,
    "lastName": last_name,
    "username": username,
    "isPatient": is_patient,
  }, ignore_token=True, ignore_middlewares=True)[0]

async def run_update_user_data(tg_id: str, auth: Auth, first_name: str = None, last_name: str = None, username: str = None):
  executor = gql.add_query("update_user_data", update_user_data())
  executor.add_fragment(gen_operation_info())
  executor.auth = auth
  data = {"tgId": f'{tg_id}'}
  if first_name:
    data['firstName'] = first_name
  if last_name:
    data['lastName'] = last_name
  if username:
    data['username'] = username
  return await executor.execute({
    "data": data
  })[0]