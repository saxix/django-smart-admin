from django.conf import settings
from django.core.signals import setting_changed
from django.dispatch import receiver
from django.utils.module_loading import import_string

_SMART_ADMIN_SECTIONS = {
    'Security': ['auth',
                 ],
    'Logs': ['admin.LogEntry',
             ],
    'Other': [],
    '_hidden_': []
}


def process_lazy(name, request=None):
    value = globals()[name]
    if isinstance(value, (list, tuple)):
        all_values = value
    elif callable(value):
        all_values = value(request)
    elif isinstance(value, (str,)):
        all_values = import_string(value)(request)
    else:
        raise ValueError(f"Invalid value `{value}` for settings.SMART_ADMIN_{name}")
    return all_values


SECTIONS = getattr(settings, 'SMART_ADMIN_SECTIONS', _SMART_ADMIN_SECTIONS)
BOOKMARKS = getattr(settings, 'SMART_ADMIN_BOOKMARKS', [])
BOOKMARKS_PERMISSION = getattr(settings, 'SMART_ADMIN_BOOKMARKS_PERMISSION', None)
ENABLE_SWITCH = getattr(settings, 'SMART_ADMIN_SWITCH', True)
PROFILE_LINK = getattr(settings, 'SMART_ADMIN_PROFILE_LINK', True)
ANYUSER_LOG = getattr(settings, 'SMART_ADMIN_ANYUSER_LOG', True)
ISROOT = getattr(settings, 'SMART_ADMIN_ISROOT', lambda request, *a: request.user.is_superuser)


@receiver(setting_changed)
def update_settings(setting, value, **kwargs):
    if setting.startswith('SMART_ADMIN_'):
        attr = setting.replace('SMART_ADMIN_', '')
        globals()[attr] = value
