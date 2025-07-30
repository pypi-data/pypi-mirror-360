from datetime import UTC
from datetime import date
from datetime import datetime
from decimal import Decimal
from math import isnan
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Final
from typing import NotRequired
from typing import TypedDict
from typing import overload

from pypdf import PdfReader
from tabula.io import read_pdf_with_template

from movslib._java import java
from movslib.model import KV
from movslib.model import ZERO
from movslib.model import Row
from movslib.model import Rows

if TYPE_CHECKING:
    from pandas import DataFrame

TEMPLATE_1: Final = f'{Path(__file__).parent}/template_1.json'
TEMPLATE_2: Final = f'{Path(__file__).parent}/template_2.json'
TEMPLATE_3: Final = f'{Path(__file__).parent}/template_3.json'


@overload
def conv_date(dt: str) -> date: ...


@overload
def conv_date(dt: float) -> None: ...


def conv_date(dt: str | float) -> date | None:
    if isinstance(dt, float):
        if not isnan(dt):
            raise TypeError(dt)
        return None
    return datetime.strptime(dt, '%d/%m/%y').replace(tzinfo=UTC).date()


@overload
def conv_decimal(dec: str) -> Decimal: ...


@overload
def conv_decimal(dec: float) -> None: ...


def conv_decimal(dec: str | float) -> Decimal | None:
    if isinstance(dec, float):
        if not isnan(dec):
            raise TypeError(dec)
        return None
    return Decimal(dec.replace('.', '').replace(',', '.'))


def read_kv(tables: 'list[DataFrame]') -> KV:
    month = tables[0].loc[0, 0]
    if not isinstance(month, str):
        raise TypeError(month)
    da = a = saldo_al = conv_date(month)

    conto_bancoposta = f'{tables[1].loc[0, 0]:012d}'
    if not isinstance(conto_bancoposta, str):
        raise TypeError(conto_bancoposta)

    intestato_a = tables[2].loc[0, 0]
    if not isinstance(intestato_a, str):
        raise TypeError(intestato_a)

    last = tables[-1]
    _, lastrow = list(last.iterrows())[-1]
    *_, accrediti, descr = lastrow.to_list()
    if not isinstance(accrediti, str):
        raise TypeError(accrediti)
    if not isinstance(descr, str):
        raise TypeError(descr)
    if descr != 'SALDO FINALE':
        raise ValueError(descr)
    saldo_contabile = saldo_disponibile = conv_decimal(accrediti)

    return KV(
        da,
        a,
        'Tutte',
        conto_bancoposta,
        intestato_a,
        saldo_al,
        ZERO if saldo_contabile is None else saldo_contabile,
        ZERO if saldo_disponibile is None else saldo_disponibile,
    )


# copyed from Row
class TRow(TypedDict):
    data_contabile: NotRequired[date]
    data_valuta: NotRequired[date]
    addebiti: NotRequired[Decimal | None]
    accrediti: NotRequired[Decimal | None]
    descrizione_operazioni: NotRequired[str]


def isnan_(obj: float | str) -> bool:
    return False if isinstance(obj, str) else isnan(obj)


class MissingContinuationError(Exception):
    def __init__(self) -> None:
        super().__init__('missing continuation')


def read_csv(tables: 'list[DataFrame]') -> list[Row]:
    ret: list[Row] = []

    for table in tables[4:]:
        t_row: TRow = {}

        def h() -> None:
            nonlocal ret
            nonlocal t_row

            if t_row and t_row['descrizione_operazioni'] not in (
                'SALDO INIZIALE',
                'SALDO FINALE',
                'TOTALE USCITE',
                'TOTALE ENTRATE',
            ):
                ret.append(Row(**t_row))
            t_row = {}

        for _, row in table.iterrows():
            try:
                data, valuta, *_, addebiti, accrediti, descr = row.to_list()
            except ValueError:  # Gennaio 2023
                continue
            if all(map(isnan_, [data, valuta, addebiti, accrediti])):
                if not t_row:
                    raise MissingContinuationError
                t_row['descrizione_operazioni'] += f' {descr}'
            else:
                h()

                t_row['data_contabile'] = conv_date(data)
                t_row['data_valuta'] = conv_date(valuta)
                t_row['addebiti'] = conv_decimal(addebiti)
                t_row['accrediti'] = conv_decimal(accrediti)
                t_row['descrizione_operazioni'] = descr
        h()

    return list(reversed(ret))


@overload
def read_estrattoconto(fn: str) -> tuple[KV, list[Row]]: ...


@overload
def read_estrattoconto(fn: str, name: str) -> tuple[KV, Rows]: ...


def read_estrattoconto(
    fn: str, name: str | None = None
) -> tuple[KV, list[Row] | Rows]:
    template = {
        1: TEMPLATE_1,
        2: TEMPLATE_2,
        3: TEMPLATE_3,
        10: TEMPLATE_2,  # dicembre
        13: TEMPLATE_2,  # marzo 2021
    }[len(PdfReader(fn).pages)]

    with java():
        tables = read_pdf_with_template(
            fn, template, pandas_options={'header': None}
        )
    if not isinstance(tables, list):
        raise TypeError(tables)
    kv = read_kv(tables)
    csv = read_csv(tables)
    return kv, (list(csv) if name is None else Rows(name, csv))
