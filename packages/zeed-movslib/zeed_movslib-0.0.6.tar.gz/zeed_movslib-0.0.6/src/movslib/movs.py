from dataclasses import fields
from datetime import UTC
from datetime import date
from datetime import datetime
from decimal import Decimal
from itertools import islice
from pathlib import Path
from typing import TYPE_CHECKING
from typing import TextIO
from typing import overload

from movslib.iterhelper import zip_with_next
from movslib.model import KV
from movslib.model import Row
from movslib.model import Rows

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Iterable


csv_field_indexes = list(zip_with_next((1, 18, 32, 50, 69), None))


def conv_date(dt: str) -> date | None:
    try:
        return datetime.strptime(dt, '%d/%m/%Y').replace(tzinfo=UTC).date()
    except ValueError:
        return None


def conv_date_inv(d: date) -> str:
    return d.strftime('%d/%m/%Y')


def read_kv(kv_file: 'Iterable[str]') -> KV:
    def next_token() -> str:
        return next(iter(kv_file)).rstrip().split(': ')[-1]

    def conv_kv_decimal(dec: str) -> Decimal:
        return Decimal(dec.replace('.', '').replace(',', '.')[:-5])

    da = conv_date(next_token())
    a = conv_date(next_token())
    tipo = next_token()
    conto_bancoposta = next_token()
    intestato_a = next_token()
    saldo_al = conv_date(next_token())
    saldo_contabile = conv_kv_decimal(next_token())
    saldo_disponibile = conv_kv_decimal(next_token())

    return KV(
        da,
        a,
        tipo,
        conto_bancoposta,
        intestato_a,
        saldo_al,
        saldo_contabile,
        saldo_disponibile,
    )


def fmt_value(
    e: None | date | Decimal | str, conv_decimal_inv: 'Callable[[Decimal], str]'
) -> str:
    if e is None:
        return ''

    if isinstance(e, date):
        return conv_date_inv(e)

    if isinstance(e, Decimal):
        return conv_decimal_inv(e)

    return str(e)


def write_kv(f: TextIO, kv: KV) -> None:
    def conv_kv_decimal_inv(d: Decimal) -> str:
        fmtd = f'{d:,}'.replace(',', '_').replace('.', ',').replace('_', '.')
        return f'+{fmtd} Euro'

    for field in fields(KV):
        field_key_str = {
            'da': ' da: (gg/mm/aaaa)',
            'a': ' a: (gg/mm/aaaa)',
            'tipo': ' Tipo(operazioni)',
            'conto_bancoposta': ' Conto BancoPosta n.',
            'intestato_a': ' Intestato a',
            'saldo_al': ' Saldo al',
            'saldo_contabile': ' Saldo contabile',
            'saldo_disponibile': ' Saldo disponibile',
        }[field.name]

        value = getattr(kv, field.name)
        kv_str = fmt_value(value, conv_kv_decimal_inv)
        f.write(f'{field_key_str}: {kv_str}\n')


class IsNoneError(ValueError):
    def __init__(self, what: None) -> None:
        super().__init__(f'{what=}')


def read_csv(csv_file: 'Iterable[str]') -> 'Iterable[Row]':
    def conv_cvs_decimal(dec: str) -> Decimal | None:
        if not dec:
            return None
        return Decimal(dec.replace('.', '').replace(',', '.'))

    for row in islice(csv_file, 1, None):
        els = (row[a:b].rstrip() for a, b in csv_field_indexes)

        data_contabile = conv_date(next(els))
        data_valuta = conv_date(next(els))
        addebiti = conv_cvs_decimal(next(els))
        accrediti = conv_cvs_decimal(next(els))
        descrizione_operazioni = next(els)

        if data_contabile is None:
            raise IsNoneError(data_contabile)
        if data_valuta is None:
            raise IsNoneError(data_valuta)

        yield Row(
            data_contabile,
            data_valuta,
            addebiti,
            accrediti,
            descrizione_operazioni,
        )


def write_csv(f: TextIO, csv: 'Iterable[Row]') -> None:
    def conv_csv_decimal_inv(d: Decimal) -> str:
        return f'{d:,}'.replace(',', '_').replace('.', ',').replace('_', '.')

    f.write(
        ' Data Contabile'
        '   Data Valuta'
        '   Addebiti (euro)'
        '   Accrediti (euro)'
        '   Descrizione operazioni\n'
    )
    for row in csv:
        f.write(' ')
        for (a, b), field in zip(csv_field_indexes, fields(Row), strict=True):
            value = getattr(row, field.name)
            row_str = fmt_value(value, conv_csv_decimal_inv)
            if b is not None:
                diff = b - a
                f.write(f'{row_str:{diff}}')
            else:
                f.write(row_str)

        f.write('\n')


@overload
def read_txt(fn: str) -> tuple[KV, list[Row]]: ...


@overload
def read_txt(fn: str, name: str) -> tuple[KV, Rows]: ...


def read_txt(fn: str, name: str | None = None) -> tuple[KV, list[Row] | Rows]:
    with Path(fn).open(encoding='UTF-8') as f:
        kv_file = islice(f, 8)
        csv_file = f
        kv = read_kv(kv_file)
        csv = read_csv(csv_file)
        return kv, (list(csv) if name is None else Rows(name, csv))


def write_txt(fn: str, kv: KV, csv: 'Iterable[Row]') -> None:
    with Path(fn).open('w', encoding='UTF-8') as f:
        write_kv(f, kv)
        write_csv(f, csv)
