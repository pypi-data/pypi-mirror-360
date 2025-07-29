# tt1

A simple Python package that prints "Hello, world!"


# steps taken:

create `__init__.py` and `setup.py` files

``` python
def say_hello():
    print("Hello, world!")
```

``` python
# setup.py
from setuptools import setup, find_packages

setup(
    name='tt1hehehaha',
    version='0.1',
    packages=find_packages(),
    author='alex uv',
    description='A simple hello world package',
    python_requires='>=3.6',
)

```


` pip install build twine`

` python -m build`

` python -m twine upload dist/*`

