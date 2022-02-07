from django.apps import AppConfig
from django.contrib.auth import get_user_model, get_permission_codename


class Config(AppConfig):
    name = 'demo'

    def ready(self):
        # from demo.admin import UserAdmin
        # from django.contrib.auth.models import Group, Permission
        # from django.contrib.contenttypes.models import ContentType
        #
        # from smart_admin.decorators import smart_register
        # from smart_admin.smart_auth.admin import ContentTypeAdmin, GroupAdmin, PermissionAdmin
        #
        # smart_register(Group)(GroupAdmin)
        # smart_register(get_user_model())(UserAdmin)
        # smart_register(Permission)(PermissionAdmin)
        # smart_register(ContentType)(ContentTypeAdmin)

        from django.contrib.auth.models import Permission
        from django.contrib.admin.models import LogEntry
        from django.contrib.contenttypes.models import ContentType
        # ct = ContentType.objects.get_for_model(LogEntry)
        # for action in ['archive', 'truncate']:
        #     opts = LogEntry._meta
        #     codename = get_permission_codename(action, opts)
        #     # FIXME: remove me (print)
        #     print(111, "apps.py:23 (get_model)", 111111, codename)
        #     label = 'Can {} {}'.format(action, opts.verbose_name_raw)
        #     params = dict(codename=codename,
        #                   content_type=ct,
        #                   defaults={'name': label[:50]})
        #     Permission.objects.get_or_create(**params)
