from __future__ import annotations

from functools import reduce
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable


def pipeline[T](*funcs: Callable[[T], T]) -> Callable[[T], T]:
    return lambda x: reduce(lambda v, f: f(v), funcs, x)
