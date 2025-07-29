from admin_extra_buttons.mixins import ExtraButtonsMixin
from django.contrib import admin

from .models import Configuration


@admin.register(Configuration)
class ConfigurationAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    pass
