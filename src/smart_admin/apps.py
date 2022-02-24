import django.contrib.admin
from django.contrib.admin.apps import AppConfig, SimpleAdminConfig
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


class SmartTemplateConfig(AppConfig):
    name = 'smart_admin'


class SmartLogsConfig(AppConfig):
    name = 'smart_admin.logs'


class SmartAuthConfig(AppConfig):
    name = 'smart_admin.smart_auth'

    def ready(self):
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType

        from smart_admin.decorators import smart_register
        from smart_admin.smart_auth.admin import ContentTypeAdmin, GroupAdmin, PermissionAdmin, UserAdmin

        smart_register(Group)(GroupAdmin)
        smart_register(get_user_model())(UserAdmin)
        smart_register(Permission)(PermissionAdmin)
        smart_register(ContentType)(ContentTypeAdmin)


class SmartConfig(SimpleAdminConfig):
    default_site = 'smart_admin.site.SmartAdminSite'
    verbose_name = _("Smart Admin")
    default = True

    def ready(self):
        super().ready()
        django.contrib.admin.autodiscover()
        from . import checks  # noqa
