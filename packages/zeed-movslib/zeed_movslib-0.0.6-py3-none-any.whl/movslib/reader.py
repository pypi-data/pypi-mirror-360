from typing import TYPE_CHECKING
from typing import Final
from typing import Protocol
from typing import overload

from movslib.buoni import read_buoni
from movslib.estrattoconto import read_estrattoconto
from movslib.libretto import read_libretto
from movslib.listamovimentixlsx import read_lista_movimenti_xlsx
from movslib.movs import read_txt
from movslib.postepay import read_postepay
from movslib.scansioni import read_scansioni

if TYPE_CHECKING:
    from movslib.model import KV
    from movslib.model import Row
    from movslib.model import Rows


class Reader(Protocol):
    @overload
    def __call__(self, fn: str) -> 'tuple[KV, list[Row]]': ...

    @overload
    def __call__(self, fn: str, name: str) -> 'tuple[KV, Rows]': ...

    def __call__(
        self, fn: str, name: str | None = None
    ) -> 'tuple[KV, list[Row] | Rows]': ...


RULES: Final[dict[str, Reader]] = {
    'ListaMovimenti.pdf': read_postepay,
    'RPOL_Movimenti_Libretto.xlsx': read_libretto,
    'RPOL_PatrimonioBuoni.xlsx': read_buoni,
    '.txt': read_txt,
    '.pdf': read_estrattoconto,
    '.scan': read_scansioni,
    '.xlsx': read_lista_movimenti_xlsx,
}


class UnsupportedSuffixError(Exception): ...


def _get_reader(fn: str) -> Reader:
    for suffix, r in RULES.items():
        if fn.endswith(suffix):
            return r

    raise UnsupportedSuffixError(fn)


@overload
def read(fn: str) -> 'tuple[KV, list[Row]]': ...


@overload
def read(fn: str, name: str) -> 'tuple[KV, Rows]': ...


def read(fn: str, name: str | None = None) -> 'tuple[KV, list[Row] | Rows]':
    reader = _get_reader(fn)
    return reader(fn) if name is None else reader(fn, name)
