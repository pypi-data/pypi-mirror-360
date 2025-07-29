# mypy: disable-error-code="no-untyped-def"
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from demo.factories import FieldDefinitionFactory, FieldsetFactory, FlexFieldFactory
from django import forms
from hope_flex_fields.models import Fieldset

from hope_smart_import.readers import open_xls, open_xls_multi
from hope_smart_import.shortcuts import validate_single, validate_xls_multi

if TYPE_CHECKING:
    from hope_smart_import.types import MultiSheetResult, SheetResult


@pytest.fixture
def xls_rdi_simple() -> "SheetResult":
    return open_xls(str((Path(__file__).parent / "data" / "rdi1.xlsx").absolute()))


@pytest.fixture
def xls_rdi() -> "MultiSheetResult":
    return open_xls_multi(str((Path(__file__).parent / "data" / "rdi1.xlsx").absolute()), [0, 1])


@pytest.fixture
def xls_missing_master() -> "MultiSheetResult":
    return open_xls_multi(str((Path(__file__).parent / "data" / "missing_master.xlsx").absolute()), [0, 1])


@pytest.fixture
def hh_validator(db: Any) -> Fieldset:
    fs = FieldsetFactory(name="household")
    FlexFieldFactory(name="household_id", fieldset=fs)
    FlexFieldFactory(name="consent_h_c", fieldset=fs)
    FlexFieldFactory(name="country_origin_h_c", fieldset=fs)
    FlexFieldFactory(name="country_h_c", fieldset=fs)
    FlexFieldFactory(name="admin1_h_c", fieldset=fs)
    FlexFieldFactory(name="admin2_h_c", fieldset=fs)
    FlexFieldFactory(name="size_h_c", fieldset=fs)
    FlexFieldFactory(name="hh_latrine_h_f", fieldset=fs)
    FlexFieldFactory(name="hh_electricity_h_f", fieldset=fs)
    FlexFieldFactory(name="registration_method_h_c", fieldset=fs)
    FlexFieldFactory(name="collect_individual_data_h_c", fieldset=fs)
    FlexFieldFactory(name="name_enumerator_h_c", fieldset=fs)
    FlexFieldFactory(name="org_enumerator_h_c", fieldset=fs)
    FlexFieldFactory(name="consent_sharing_h_c", fieldset=fs)
    FlexFieldFactory(name="first_registration_date_h_c", fieldset=fs)
    return fs


@pytest.fixture
def simple_validator(db: Any) -> Fieldset:
    fs = FieldsetFactory()
    FlexFieldFactory(name="name", fieldset=fs)
    FlexFieldFactory(name="last_name", fieldset=fs)
    return fs


@pytest.fixture
def ind_validator(db: Any) -> Fieldset:
    fs = FieldsetFactory(name="individual")
    FlexFieldFactory(name="household_id", fieldset=fs)
    FlexFieldFactory(name="relationship_i_c", fieldset=fs)
    FlexFieldFactory(name="full_name_i_c", fieldset=fs)
    FlexFieldFactory(name="given_name_i_c", fieldset=fs)
    FlexFieldFactory(name="middle_name_i_c", fieldset=fs)
    FlexFieldFactory(name="family_name_i_c", fieldset=fs)
    FlexFieldFactory(name="photo_i_c", fieldset=fs)
    FlexFieldFactory(
        name="gender_i_c",
        fieldset=fs,
        definition=FieldDefinitionFactory(field_type=forms.ChoiceField),
        attrs={"choices": [["FEMALE", "FEMALE"], ["MALE", "MALE"]]},
    )

    FlexFieldFactory(
        name="birth_date_i_c",
        fieldset=fs,
        definition=FieldDefinitionFactory(field_type=forms.DateField),
    )
    FlexFieldFactory(name="estimated_birth_date_i_c", fieldset=fs)
    FlexFieldFactory(name="national_id_no_i_c", fieldset=fs)
    FlexFieldFactory(name="national_id_photo_i_c", fieldset=fs)
    FlexFieldFactory(name="national_id_issuer_i_c", fieldset=fs)
    FlexFieldFactory(name="phone_no_i_c", fieldset=fs)
    FlexFieldFactory(name="primary_collector_id", fieldset=fs)
    FlexFieldFactory(name="alternate_collector_id", fieldset=fs)
    FlexFieldFactory(name="first_registration_date_i_c", fieldset=fs)
    FlexFieldFactory(
        name="disability_i_c",
        fieldset=fs,
        definition=FieldDefinitionFactory(field_type=forms.ChoiceField),
        attrs={"choices": [["not disabled", "not disabled"], ["disabled", "disabled"]]},
    )
    return fs


def test_validate_simple(xls_rdi_simple: "SheetResult", hh_validator: Fieldset, ind_validator: Fieldset) -> None:
    hh_validator.set_primary_key_col("household_id")
    ind_validator.set_master(hh_validator, "household_id")

    errors = validate_single(xls_rdi_simple, hh_validator, fail_if_alien=True)

    assert errors == {}


def test_validate_multi(xls_rdi: "MultiSheetResult", hh_validator: Fieldset, ind_validator: Fieldset) -> None:
    errors = validate_xls_multi(xls_rdi, [hh_validator, ind_validator], fail_if_alien=True)
    assert errors == {"1:household": {}, "2:individual": {}}


def test_validate_master_detail(xls_rdi: "MultiSheetResult", hh_validator: Fieldset, ind_validator: Fieldset) -> None:
    hh_validator.set_primary_key_col("household_id")
    ind_validator.set_master(hh_validator, "household_id")

    errors = validate_xls_multi(xls_rdi, [hh_validator, ind_validator], fail_if_alien=True)
    assert errors == {"1:household": {}, "2:individual": {}}


def test_validate_missing_master(
    xls_missing_master: "MultiSheetResult",
    hh_validator: Fieldset,
    ind_validator: Fieldset,
) -> None:
    hh_validator.set_primary_key_col("household_id")
    ind_validator.set_master(hh_validator, "household_id")

    errors = validate_xls_multi(xls_missing_master, [hh_validator, ind_validator], fail_if_alien=True)

    assert errors["2:individual"] == {2: {"-": ["'missing' not found in master"]}}
    assert errors["1:household"] == {}
