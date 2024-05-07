from py_simple_graphql.utils import gen_query
from tests.m_types import Directional

def directionals():
  return gen_query(
    name="directionalsDel",
    request="...name",
    require_fragments = ['name'],
    to_type=Directional,
    q_words="data.directionalsDel[:].{name_r: name}"
  )