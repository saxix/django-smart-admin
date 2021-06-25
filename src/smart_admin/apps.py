import django.contrib.admin
from django.contrib.admin.apps import SimpleAdminConfig

from django.utils.translation import gettext_lazy as _


class SmartConfig(SimpleAdminConfig):
    default_site = 'smart_admin.site.SmartAdminSite'
    verbose_name = _("Smart Admin")

    def ready(self):
        super().ready()
        django.contrib.admin.autodiscover()
