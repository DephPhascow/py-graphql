from setuptools import setup, find_packages

 
setup(
    name = "py_simple_graphql",
    version = "1.1.1",
    keywords = ("graphql", ),
    description = "Simple work with GraphQL",
    long_description = "Simple work with GraphQL",
    license = "MIT Licence",
 
    url = "https://github.com/DephPhascow/py-graphql",
    author = "DephPhascow",
    author_email = "d.sinisterpsychologist@gmail.com",
 
    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["requests", 'aiohttp', 'strenum', 'jmespath']
)