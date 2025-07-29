from typing import Any, Optional

import factory
from django import forms
from django.contrib.auth.models import Group, Permission, User
from factory.django import DjangoModelFactory
from factory.faker import Faker
from hope_flex_fields.models import DataChecker, Fieldset, FlexField
from hope_flex_fields.models.definition import FieldDefinition
from strategy_field.utils import fqn

from hope_smart_import.models import Configuration


class FieldsetFactory(DjangoModelFactory):
    extends = None

    class Meta:
        model = Fieldset


class FieldDefinitionFactory(DjangoModelFactory):
    field_type = fqn(forms.CharField)

    class Meta:
        model = FieldDefinition
        django_get_or_create = ("field_type",)


class FlexFieldFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"FlexField {n}")
    fieldset = factory.SubFactory(Fieldset)
    definition = factory.SubFactory(FieldDefinitionFactory)

    class Meta:
        model = FlexField


class DataCheckerFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"DataChecker {n}")

    class Meta:
        model = DataChecker

    @factory.post_generation  # type: ignore[misc]
    def fieldsets(self, create: bool, extracted: list[str], **kwargs: Any) -> None:
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for perm_name in extracted:
                app, perm = perm_name.split(".")
                self.fieldsets.add(Permission.objects.get(content_type__app_label=app, codename=perm))


class ConfigurationFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Configuration {n}")

    class Meta:
        model = Configuration


class UserFactory(DjangoModelFactory):
    username = factory.Sequence(lambda n: f"User {n}")
    email = factory.Sequence(lambda n: f"email{n}@example.com")

    class Meta:
        model = User


class GroupFactory(DjangoModelFactory):
    name = Faker("name")

    class Meta:
        model = Group
        django_get_or_create = ("name",)

    @factory.post_generation  # type: ignore[misc]
    def permissions(self, create: bool, extracted: list[str], **kwargs: Any) -> None:
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for perm_name in extracted:
                app, perm = perm_name.split(".")
                self.permissions.add(Permission.objects.get(content_type__app_label=app, codename=perm))


class user_grant_permission:  # noqa
    def __init__(self, user: User, permissions: Optional[list[str]] = None):
        self.user = user
        self.permissions = permissions
        self.group = None

    def __enter__(self):
        if hasattr(self.user, "_group_perm_cache"):
            del self.user._group_perm_cache
        if hasattr(self.user, "_perm_cache"):
            del self.user._perm_cache
        self.group = GroupFactory(permissions=self.permissions or [])
        self.user.groups.add(self.group)

    def __exit__(self, *exc_info):
        if self.group:
            self.user.groups.remove(self.group)
            self.group.delete()

    def start(self):
        """Activate a patch, returning any created mock."""
        return self.__enter__()

    def stop(self):
        """Stop an active patch."""
        return self.__exit__()
