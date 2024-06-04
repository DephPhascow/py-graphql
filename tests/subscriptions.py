
from py_simple_graphql.utils import gen_subscription


def my_name():
    return gen_subscription(
        id="whatsMyName",
        name="whatsMyName"
    )