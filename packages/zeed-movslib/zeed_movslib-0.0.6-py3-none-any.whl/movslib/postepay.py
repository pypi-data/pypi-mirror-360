from datetime import UTC
from datetime import date
from datetime import datetime
from decimal import Decimal
from locale import LC_ALL
from locale import setlocale
from math import isnan
from typing import Final
from typing import overload

from tabula.io import read_pdf

from movslib._java import java
from movslib.model import KV
from movslib.model import Row
from movslib.model import Rows


def conv_date(dt: str) -> date:
    return datetime.strptime(dt, '%d/%m/%Y').replace(tzinfo=UTC).date()


def conv_kv_date(dt: str) -> date:
    orig = setlocale(LC_ALL)
    setlocale(LC_ALL, 'it_IT.utf8')
    try:
        return datetime.strptime(dt, '%d %B %Y').replace(tzinfo=UTC).date()
    finally:
        setlocale(LC_ALL, orig)


@overload
def conv_decimal(dec: str) -> Decimal: ...


@overload
def conv_decimal(dec: float) -> None: ...


def conv_decimal(dec: str | float) -> Decimal | None:
    if isinstance(dec, float):
        if not isnan(dec):
            raise TypeError(dec)
        return None
    return Decimal(dec.replace('.', '').replace(',', '.').replace('€', ''))


def read_kv(fn: str) -> KV:
    with java():
        tables = read_pdf(
            fn,
            pandas_options={'header': None},
            pages=1,
            area=[[0, 400, 100, 600], [140, 120, 170, 210], [170, 0, 200, 600]],
            silent=True,
        )
    if not isinstance(tables, list):
        raise TypeError(tables)
    data, numero_intestato, saldi = tables

    tipo = numero_intestato.loc[0, 0]
    if not isinstance(tipo, str):
        raise TypeError(tipo)
    conto_bancoposta = numero_intestato.loc[1, 0]
    if not isinstance(conto_bancoposta, str):
        raise TypeError(conto_bancoposta)
    intestato_a = data.loc[0, 0]
    if not isinstance(intestato_a, str):
        raise TypeError(intestato_a)
    saldo_contabile = saldi.loc[0, 3]
    if not isinstance(saldo_contabile, str):
        raise TypeError(saldo_contabile)
    saldo_disponibile = saldi.loc[0, 5]
    if not isinstance(saldo_disponibile, str):
        raise TypeError(saldo_disponibile)
    return KV(
        None,
        None,
        '',
        tipo,
        conto_bancoposta,
        conv_kv_date(' '.join(intestato_a.split()[:3])),
        conv_decimal(saldo_contabile),
        conv_decimal(saldo_disponibile),
    )


def read_csv(fn: str) -> list[Row]:
    with java():
        tables = read_pdf(fn, pages='all', lattice=True, silent=True)
    if not isinstance(tables, list):
        raise TypeError(tables)
    n: Final = 5
    tables = [table for table in tables if len(table.columns) == n]
    tables[0].drop(index=0, inplace=True)

    ret: list[Row] = []
    for table in tables:
        for dc, dv, do, ad, ac in table.itertuples(index=False):
            ret.append(
                Row(
                    conv_date(dc),
                    conv_date(dv),
                    conv_decimal(ad),
                    conv_decimal(ac),
                    do.replace('\r', ' '),
                )
            )
    return ret


@overload
def read_postepay(fn: str) -> tuple[KV, list[Row]]: ...


@overload
def read_postepay(fn: str, name: str) -> tuple[KV, Rows]: ...


def read_postepay(
    fn: str, name: str | None = None
) -> tuple[KV, list[Row] | Rows]:
    kv = read_kv(fn)
    csv = read_csv(fn)

    return kv, (list(csv) if name is None else Rows(name, csv))
