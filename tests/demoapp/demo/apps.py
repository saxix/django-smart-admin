from django.apps import AppConfig
from django.contrib.auth import get_user_model


class Config(AppConfig):
    name = 'demo'

    def ready(self):
        from demo.admin import UserAdmin
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType

        from smart_admin.decorators import smart_register
        from smart_admin.smart_auth.admin import ContentTypeAdmin, GroupAdmin, PermissionAdmin

        smart_register(Group)(GroupAdmin)
        smart_register(get_user_model())(UserAdmin)
        smart_register(Permission)(PermissionAdmin)
        smart_register(ContentType)(ContentTypeAdmin)
