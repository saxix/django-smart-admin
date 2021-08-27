import django.contrib.admin
from django.contrib.admin.apps import SimpleAdminConfig, AppConfig
from django.contrib.auth import get_user_model

from django.utils.translation import gettext_lazy as _


class SmartTemplateConfig(AppConfig):
    name = 'smart_admin'


class SmartLogsConfig(AppConfig):
    name = 'smart_admin.logs'


class SmartAuthConfig(AppConfig):
    name = 'smart_admin.smart_auth'

    def ready(self):
        from smart_admin.smart_auth.admin import GroupAdmin, UserAdmin, PermissionAdmin, ContentTypeAdmin
        from smart_admin.decorators import smart_register
        from django.contrib.auth.models import Group, Permission
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

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
