# mypy: disable-error-code="no-untyped-def"
from pathlib import Path
from typing import Any, Iterable

import pytest
from demo.factories import FieldsetFactory, FlexFieldFactory
from hope_flex_fields.models import Fieldset

from hope_smart_import.readers import open_xls, open_xls_multi
from hope_smart_import.shortcuts import validate_single, validate_xls_multi


@pytest.fixture
def xls_simple() -> Iterable:
    return open_xls(str((Path(__file__).parent / "data" / "r1.xlsx").absolute()))


@pytest.fixture
def xls_multi() -> Iterable:
    return open_xls_multi(str((Path(__file__).parent / "data" / "r1.xlsx").absolute()), [0, 1])


@pytest.fixture
def simple_validator(db: Any) -> Fieldset:
    fs = FieldsetFactory(name="Simple Validator")
    FlexFieldFactory(name="name", fieldset=fs)
    FlexFieldFactory(name="last_name", fieldset=fs)
    return fs


def test_validate_simple(xls_simple: Iterable, simple_validator: Fieldset):
    g1 = list(xls_simple)
    errors = validate_single(g1, simple_validator, fail_if_alien=False)
    assert not errors

    errors = validate_single(g1, simple_validator, fail_if_alien=True)
    assert errors == {
        1: {"-": ["Alien values found {'gender'}"]},
        2: {"-": ["Alien values found {'gender'}"]},
    }


def test_validate_xls_multi(xls_multi: Iterable, simple_validator) -> None:
    errors = validate_xls_multi(xls_multi, [simple_validator, simple_validator], fail_if_alien=True)
    assert errors == {
        "1:Simple Validator": {
            1: {"-": ["Alien values found {'gender'}"]},
            2: {"-": ["Alien values found {'gender'}"]},
        },
        "2:Simple Validator": {
            1: {"-": ["Alien values found {'gender'}"]},
            2: {"-": ["Alien values found {'gender'}"]},
        },
    }
