
from py_simple_graphql.utils import gen_subscription


def get_count():
    return gen_subscription(
        "getCount",
        "count",
        var={
            "target": "Int!"
        },
    )