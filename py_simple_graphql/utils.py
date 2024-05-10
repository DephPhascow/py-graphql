import json
from typing import List

from py_simple_graphql.gql_type import GQLType
from py_simple_graphql.models import Errors, Error
from py_simple_graphql.enums import QueryType
from py_simple_graphql.query import Query, QueryFragment
import jmespath


def get_data(data: dict, method_name: str, query: str = None):
    if isinstance(data, str):
        data = json.loads(data)
    jsonpath_expression = jmespath.search(query or f'data.{method_name}', data)
    return jsonpath_expression

def check_errors(data: dict):
    if "errors" in data:
        errors = []
        for error in data["errors"]:
            errors.append(Error(**error))
        raise Errors(errors)
    
def gen_sub_funct(query_type: QueryType, name: str, request: str, var: dict, require_fragments: List[str] = [], q_words: str = None, to_type: GQLType = None, id: str = None):
    for key in list(var.keys()):
        if key[0] != "$":
            var[f"${key}"] = var.pop(key)
    return Query(query_type=query_type,
        id=id,
        query_name = name,
        query_request = request,
        variables = var,
        init_args_from_vars = True,
        require_fragments = require_fragments,
        q_words = q_words,
        to_type = to_type,
    )
    

def gen_query(name: str, request: str = "", var: dict = {}, require_fragments: List[str] = [], q_words: str = None, to_type: GQLType = None):
  return gen_sub_funct(QueryType.QUERY, name, request, var, require_fragments, q_words, to_type)

def gen_mutate(name: str, request: str = "", var: dict = {}, require_fragments: List[str] = [], q_words: str = None, to_type: GQLType = None):
  return gen_sub_funct(QueryType.MUTATION, name, request, var, require_fragments, q_words, to_type)

def gen_send_file(name: str, request: str = "", var: dict = {}, require_fragments: List[str] = [], q_words: str = None, to_type: GQLType = None):
  return gen_sub_funct(QueryType.SEND_FILE, name, request, var, require_fragments, q_words, to_type)

def gen_subscription(id: str, name: str, request: str = "", var: dict = {}, require_fragments: List[str] = [], q_words: str = None, to_type: GQLType = None):
    return gen_sub_funct(QueryType.SUBSCRIPTION, name, request, var, require_fragments, q_words, to_type, id)

def gen_fragment(name: str, type_name: str, request: str):
    return QueryFragment(
        query_name = name,
        query_request = request,
        type_name = type_name,
        init_args_from_vars = True
    )