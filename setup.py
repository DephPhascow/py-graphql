from dotenv import load_dotenv
from os import getenv
from setuptools import setup, find_packages
 
load_dotenv()

EMAIL = getenv("EMAIL")
AUTHOR = getenv("AUTHOR")
 
setup(
    name = "py_simple_graphql",
    version = "1.2.0",
    keywords = ("graphql", ),
    description = "Simple work with GraphQL",
    long_description = "Simple work with GraphQL",
    license = "MIT Licence",
 
    url = "https://github.com/DephPhascow/py-graphql",
    author = AUTHOR,
    author_email = EMAIL,
 
    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["requests", 'strenum; python_version < "3.10"']
)