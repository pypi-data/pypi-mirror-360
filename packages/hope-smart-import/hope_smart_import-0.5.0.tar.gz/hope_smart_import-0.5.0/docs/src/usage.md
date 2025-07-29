# Usage


## Simple usage in code

Let imagine a simple `test.xlsx` file with this structure


| name | last_name | gender |
|------|-----------|--------|
| John | Doe       | M      |
| Jane | Doe       | F      |
| Mary | Error     | X      |

1. Let start creating validation rules (here in the code, you can use the admin interface otherwise)


        fs, __ = Fieldset.objects.get_or_create(name="test.xlsx")

        charfield = FieldDefinition.objects.get(field_type=forms.CharField)
        choicefield = FieldDefinition.objects.get(field_type=forms.ChoiceField)

        FlexField.objects.get_or_create(name="name", fieldset=fs, field=charfield)
        FlexField.objects.get_or_create(name="last_name", fieldset=fs, field=charfield)
        FlexField.objects.get_or_create(name="gender", fieldset=fs, field=choicefield,
                                        attrs={"choices": [["M", "M"], ["F", "F"]]})


2. Validate the file against it

        errors = validate_xls(xls_simple, fs, fail_if_alien=True)
        print(errors)

```python
{3: {'gender': ['Select a valid choice. X is not one of the available choices.']}}

```
