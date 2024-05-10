from py_simple_graphql.utils import gen_fragment

def fragment_user():
    return gen_fragment(
        name="namer",
        request="name",
        type_name="DirectionModelType",
    )