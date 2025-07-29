import csv
from collections.abc import Callable
from itertools import islice
from typing import TYPE_CHECKING, Any, Iterable

import openpyxl

if TYPE_CHECKING:
    from openpyxl.workbook.workbook import Workbook
    from openpyxl.worksheet.worksheet import Worksheet

    from .types import MultiSheetResult, SheetResult, ValueMapper


def identity(x: Any) -> Any:
    return x


def _read_worksheet(
    sheet: "Worksheet",
    start_at: int,
    headers: bool,
    value_mapper: Callable[[Any], Any] = identity,
) -> Iterable[dict[str, Any]]:
    rows = sheet.rows

    field_names = None
    generate_field_names = False
    if headers:
        field_names = [str(cell.value) for cell in next(rows)]
    else:
        generate_field_names = True

    rows = islice(rows, start_at, None)
    for row in rows:
        if generate_field_names:
            field_names = [f"column{d + 1}" for d in range(len(row))]

        yield dict(zip(field_names, (value_mapper(cell.value) for cell in row), strict=True))


def open_xls(
    filepath: str,
    *,
    sheet_index: int = 0,
    start_at: int = 0,
    headers: bool = True,
    value_mapper: "ValueMapper" = identity,
) -> "SheetResult":
    wb: "Workbook" = openpyxl.load_workbook(filepath)
    sh: "Worksheet" = wb.worksheets[sheet_index]
    yield from _read_worksheet(sh, start_at=start_at, headers=headers, value_mapper=value_mapper)


def open_xls_multi(
    filepath: str,
    sheets: list[int] = (0,),
    start_at: list[int] | int = 0,
    headers: list[bool] | bool = True,
    value_mapper: "ValueMapper" = identity,
) -> "MultiSheetResult":
    wb: "Workbook" = openpyxl.load_workbook(filepath)
    for si in sheets:
        sh: "Worksheet" = wb.worksheets[si]
        start_at = start_at if isinstance(start_at, int) else start_at[si]
        headers = headers if isinstance(headers, bool) else headers[si]
        yield (
            si,
            _read_worksheet(sh, start_at=start_at, headers=headers, value_mapper=value_mapper),
        )


def open_csv(
    filepath: str,
    *,
    start_at: int = 0,
    headers: bool = False,
    value_mapper: "ValueMapper" = identity,
) -> "SheetResult":
    with open(filepath) as f:
        if headers:
            reader = csv.DictReader(f)
            reader = islice(reader, start_at, None)
            for row in reader:
                yield {k: value_mapper(v) for k, v in row.items()}
        else:
            reader = csv.reader(f)
            reader = islice(reader, start_at, None)
            for row in reader:
                field_names = [f"column{d + 1}" for d in range(len(row))]
                yield dict(zip(field_names, map(value_mapper, row), strict=True))
