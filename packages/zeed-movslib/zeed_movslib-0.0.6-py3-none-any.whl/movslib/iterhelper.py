from itertools import chain
from itertools import pairwise
from typing import TYPE_CHECKING
from typing import cast
from typing import overload

if TYPE_CHECKING:
    from collections.abc import Iterable


@overload
def zip_with_next[T](
    it: 'Iterable[T]', last: None
) -> 'Iterable[tuple[T, T | None]]': ...
@overload
def zip_with_next[T](it: 'Iterable[T]', last: T) -> 'Iterable[tuple[T, T]]': ...
def zip_with_next[T](
    it: 'Iterable[T]', last: T | None
) -> 'Iterable[tuple[T, T | None]]':
    return cast('Iterable[tuple[T, T | None]]', pairwise(chain(it, (last,))))
