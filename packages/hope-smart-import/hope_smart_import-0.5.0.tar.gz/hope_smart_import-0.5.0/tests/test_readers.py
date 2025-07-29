from collections.abc import Callable
from pathlib import Path
from typing import Any, TYPE_CHECKING

import pytest

from hope_smart_import.readers import open_csv, open_xls, open_xls_multi

if TYPE_CHECKING:
    from hope_smart_import.types import ValueMapper


@pytest.fixture
def xls() -> str:
    return str((Path(__file__).parent / "data" / "r1.xlsx").absolute())


@pytest.fixture
def csv() -> str:
    return str((Path(__file__).parent / "data" / "r1.csv").absolute())


@pytest.mark.parametrize("start_at", [0, 1])
def test_read_csv_headers(csv: str, start_at: int) -> None:
    for e in open_csv(csv, start_at=start_at, headers=True):
        assert list(e.keys()) == ["name", "last_name", "gender"]


@pytest.mark.parametrize("start_at", [0, 1])
def test_read_csv_no_headers(csv: str, start_at: int) -> None:
    for e in open_csv(csv, start_at=start_at, headers=False):
        assert list(e.keys()) == ["column1", "column2", "column3"]


@pytest.mark.parametrize(("mapper", "validator"), [(str.upper, str.isupper), (str.lower, str.islower)])
def test_read_csv_value_mapper(csv: str, mapper: "ValueMapper", validator: Callable[[Any], bool]) -> None:
    for row in open_csv(csv, headers=True, value_mapper=mapper):
        assert all(map(validator, row.values()))


@pytest.mark.parametrize("start_at", [0, 1])
def test_read_xls_headers(xls: str, start_at: int) -> None:
    for e in open_xls(xls, start_at=start_at):
        assert list(e.keys()) == ["name", "last_name", "gender"]


@pytest.mark.parametrize("start_at", [0, 1])
def test_read_xls_no_headers(xls: str, start_at: int) -> None:
    for e in open_xls(xls, start_at=start_at, headers=False):
        assert list(e.keys()) == ["column1", "column2", "column3"]


@pytest.mark.parametrize(("mapper", "validator"), [(str.upper, str.isupper), (str.lower, str.islower)])
def test_read_xls_value_mapper(xls: str, mapper: "ValueMapper", validator: Callable[[Any], bool]) -> None:
    for row in open_xls(xls, headers=True, value_mapper=mapper):
        assert all(map(validator, row.values()))


@pytest.mark.parametrize("start_at", [0, 1])
def test_read_multi_xls_headers(xls: str, start_at: int) -> None:
    ret = []
    for e, sh in open_xls_multi(xls, sheets=[0, 1], start_at=start_at, headers=True):
        ret.extend([(e, row) for row in sh])
    if start_at == 0:
        # Sheet 0 - Row 0
        assert ret[0] == (0, {"name": "John", "last_name": "Doe", "gender": "M"})
        # Sheet 0 - Row 1
        assert ret[1] == (0, {"name": "Jane", "last_name": "Doe", "gender": "F"})
        # Sheet 1 - Row 0
        assert ret[2] == (1, {"name": "John1", "last_name": "Doe1", "gender": "m"})
        # Sheet 1 - Row 1
        assert ret[3] == (1, {"name": "Jane1", "last_name": "Doe1", "gender": "f"})
    if start_at == 1:
        # Sheet 0 - Row 0
        assert ret[0] == (0, {"name": "Jane", "last_name": "Doe", "gender": "F"})
        # Sheet 1 - Row 1
        assert ret[1] == (1, {"name": "Jane1", "last_name": "Doe1", "gender": "f"})


@pytest.mark.parametrize(("mapper", "validator"), [(str.upper, str.isupper), (str.lower, str.islower)])
def test_read_multi_xls_value_mapper(xls: str, mapper: "ValueMapper", validator: Callable[[Any], bool]) -> None:
    for _, sheet in open_xls_multi(xls, sheets=[0, 1], headers=True, value_mapper=mapper):
        for row in sheet:
            assert all(map(validator, row.values()))
