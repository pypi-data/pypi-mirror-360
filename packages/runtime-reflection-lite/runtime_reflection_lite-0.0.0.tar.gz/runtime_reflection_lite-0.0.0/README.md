[![Test](https://github.com/apmadsen/runtime-reflection-lite/actions/workflows/python-test.yml/badge.svg)](https://github.com/apmadsen/runtime-reflection-lite/actions/workflows/python-test.yml)
[![Coverage](https://github.com/apmadsen/runtime-reflection-lite/actions/workflows/python-test-coverage.yml/badge.svg)](https://github.com/apmadsen/runtime-reflection-lite/actions/workflows/python-test-coverage.yml)
[![Stable Version](https://img.shields.io/pypi/v/runtime-reflection-lite?label=stable&sort=semver&color=blue)](https://github.com/apmadsen/runtime-reflection-lite/releases)
![Pre-release Version](https://img.shields.io/github/v/release/apmadsen/runtime-reflection-lite?label=pre-release&include_prereleases&sort=semver&color=blue)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/runtime-reflection-lite)
[![PyPI Downloads](https://static.pepy.tech/badge/runtime-reflection-lite/week)](https://pepy.tech/projects/runtime-reflection-lite)

# runtime-reflection-lite

This project is meant as a light implementation of the later runtime-reflection project which will support deeper reflection of the source code. As such, it contains the bare minimum to reflect on functions and resolve type annotations.

### Example

```python
from runtime.reflection.lite import reflect_function

class Class1:
     def __init__(self, value: str):
          self.__value = value

     def do_something(self, suffix: str | None = None) -> str:
          return self.__value + (suffix or "")

signature1 = reflect_function(Class1.do_something) # -> (suffix: str | None) -> str
signature2 = reflect_function(Class1.__init__) # -> (value: str)
```

## Full documentation

[Go to documentation](https://github.com/apmadsen/runtime-reflection-lite/blob/main/docs/documentation.md)