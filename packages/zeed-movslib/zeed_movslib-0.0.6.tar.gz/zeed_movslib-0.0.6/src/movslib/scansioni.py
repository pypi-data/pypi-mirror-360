from datetime import UTC
from datetime import date
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import overload

from movslib.model import KV
from movslib.model import Row
from movslib.model import Rows


def parse_date(raw: str) -> date | None:
    if not raw.strip():
        return None
    return datetime.strptime(raw.strip(), '%d/%m/%y').replace(tzinfo=UTC).date()


def parse_decimal(raw: str) -> Decimal | None:
    if not raw.strip():
        return None
    return Decimal(raw.rstrip().replace('.', '').replace(',', '.'))


def parse_row(row: str) -> Row:
    return Row(
        parse_date(row[0:12]) or date.min,
        parse_date(row[12:24]) or date.min,
        parse_decimal(row[24:36]),
        parse_decimal(row[36:48]),
        row[48:-2].rstrip(),
    )


@overload
def read_scansioni(fn: str) -> tuple[KV, list[Row]]: ...


@overload
def read_scansioni(fn: str, name: str) -> tuple[KV, Rows]: ...


def read_scansioni(
    fn: str, name: str | None = None
) -> tuple[KV, list[Row] | Rows]:
    with Path(fn).open() as f:
        all_rows = [parse_row(row) for row in f]

    iniziale, *rows, finale = all_rows
    rows.reverse()

    kv = KV(
        iniziale.data_contabile,
        finale.data_contabile,
        '',
        '',
        '',
        finale.data_contabile,
        iniziale.money,
        finale.money,
    )
    return kv, (rows if name is None else Rows(name, rows))
