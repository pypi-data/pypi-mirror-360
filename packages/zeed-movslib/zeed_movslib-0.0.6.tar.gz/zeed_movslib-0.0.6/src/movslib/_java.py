from contextlib import contextmanager
from os import environ
from typing import TYPE_CHECKING

from jdk4py import JAVA_HOME

if TYPE_CHECKING:
    from collections.abc import Iterator


@contextmanager
def java() -> 'Iterator[None]':
    _orig = environ.get('JAVA_HOME', default=None)
    environ['JAVA_HOME'] = str(JAVA_HOME)
    try:
        yield
    finally:
        if _orig is None:
            del environ['JAVA_HOME']
        else:
            environ['JAVA_HOME'] = _orig
