# mypy: disable-error-code="no-untyped-def"
from pathlib import Path

import pytest
from django import forms
from hope_flex_fields.models import Fieldset
from hope_flex_fields.models.definition import FieldDefinition
from hope_flex_fields.models.flexfield import FlexField

from hope_smart_import.readers import open_xls
from hope_smart_import.shortcuts import validate_single


@pytest.fixture
def xls_path() -> str:
    return str((Path(__file__).parent / "data" / "simple2.xlsx").absolute())


def test_sample_code(db, xls_path):
    fs, __ = Fieldset.objects.get_or_create(name="test.xlsx")

    charfield = FieldDefinition.objects.get(field_type=forms.CharField)
    choicefield = FieldDefinition.objects.get(field_type=forms.ChoiceField)

    FlexField.objects.get_or_create(name="name", fieldset=fs, definition=charfield)
    FlexField.objects.get_or_create(name="last_name", fieldset=fs, definition=charfield)
    FlexField.objects.get_or_create(
        name="gender",
        fieldset=fs,
        definition=choicefield,
        attrs={"choices": [["M", "M"], ["F", "F"]]},
    )

    errors = validate_single(open_xls(xls_path), fs, fail_if_alien=True)
    assert errors == {3: {"gender": ["Select a valid choice. X is not one of the available choices."]}}
