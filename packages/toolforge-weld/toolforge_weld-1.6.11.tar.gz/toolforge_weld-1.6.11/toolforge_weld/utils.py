from __future__ import annotations

import itertools
from typing import Iterator, Tuple, TypeVar

import requests

import toolforge_weld

T = TypeVar("T")

USER_AGENT = f"toolforge_weld/{toolforge_weld.__version__} python-requests/{requests.__version__}"


def peek(iterable: Iterator[T]) -> Tuple[T | None, Iterator[T]]:
    """Returns a tuple with the first element from an iterator and the iterator itself without consuming the first
    element."""
    try:
        first = next(iterable)
    except StopIteration:
        return None, iter([])
    return first, itertools.chain([first], iterable)
