from py_simple_graphql.utils import gen_query
from tests.m_types import Directional

def directionals():
  return gen_query(
    name="directionalsDel",
    request="...namer",
    require_fragments = ['namer'],
    to_type=Directional,
    q_words="data.directionalsDel[:].{name_r: name}"
  )
  
def users():
  return gen_query(
    name="users",
    request="tgId",
    q_words="data.users[:].tgId"
  )