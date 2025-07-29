from collections.abc import Callable, Iterable
from typing import Any

RowResult = dict[str, str]
SheetResult = Iterable[RowResult]
MultiSheetResult = Iterable[tuple[int, SheetResult]]
ValueMapper = Callable[[Any], Any]
