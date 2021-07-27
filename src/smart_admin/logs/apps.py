from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SmartConfig(AppConfig):
    name = 'smart_admin.logs'
    verbose_name = _("Admin Log")

    def ready(self):
        super().ready()
