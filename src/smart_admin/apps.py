import django.contrib.admin
from django.contrib.admin.apps import SimpleAdminConfig, AppConfig

from django.utils.translation import gettext_lazy as _


class SmartTemplateConfig(AppConfig):
    name = 'smart_admin'


class SmartConfig(SimpleAdminConfig):
    default_site = 'smart_admin.site.SmartAdminSite'
    verbose_name = _("Smart Admin")
    default = True

    def ready(self):
        super().ready()
        django.contrib.admin.autodiscover()
