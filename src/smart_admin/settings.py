from django.conf import settings
from django.core.signals import setting_changed
from django.dispatch import receiver
from django.utils.functional import lazy
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

_SMART_ADMIN_SECTIONS = {
    'Security': ['auth',
                 ],
    'Logs': ['admin.LogEntry',
             ],
    'Other': [],
    '_hidden_': []
}


def process_setting(value, request):
    if callable(value):
        return value(request)
    elif isinstance(value, (str,)) and '.' in value:
        return import_string(value)(request)
    else:
        return value


def get_bookmarks(request=None):
    raw_value = getattr(settings, 'SMART_ADMIN_BOOKMARKS', [])
    values = process_setting(raw_value, request)
    if not isinstance(values, (list, tuple)):
        raise ValueError(f"Invalid value `{values}` for settings.SMART_ADMIN_BOOKMARKS")
    return values


def check_logentry_archive_perm(request, perm, **kwargs):
    if LOGENTRY_ARCHIVE_PERM:
        return request.user.has_perm(LOGENTRY_ARCHIVE_PERM)
    return True


TITLE = getattr(settings, 'SMART_ADMIN_TITLE', _('Django site admin'))
HEADER = getattr(settings, 'SMART_ADMIN_HEADER', _('Django administration'))

SECTIONS = getattr(settings, 'SMART_ADMIN_SECTIONS', _SMART_ADMIN_SECTIONS)
BOOKMARKS = getattr(settings, 'SMART_ADMIN_BOOKMARKS', [])
BOOKMARKS_PERMISSION = getattr(settings, 'SMART_ADMIN_BOOKMARKS_PERMISSION', None)
ENABLE_SWITCH = getattr(settings, 'SMART_ADMIN_SWITCH', True)
PROFILE_LINK = getattr(settings, 'SMART_ADMIN_PROFILE_LINK', True)
ANYUSER_LOG = getattr(settings, 'SMART_ADMIN_ANYUSER_LOG', True)
ISROOT = getattr(settings, 'SMART_ADMIN_ISROOT', lambda request, *a: request.user.is_superuser)
SYSINFO_TTL = getattr(settings, 'SMART_ADMIN_SYSINFO_TTL', 60)
LOGS_RETENTION_DAYS = getattr(settings, 'SMART_ADMIN_LOGS_RETENTION_DAYS', 365)
MODEL_LABEL_FORMAT = getattr(settings, 'SMART_ADMIN_MODEL_LABEL_FORMAT', '{model[name]} ({app[name]})')
LOGENTRY_ARCHIVE_PERM = getattr(settings, 'LOGENTRY_ARCHIVE_PERM', None)


@receiver(setting_changed)
def update_settings(setting, value, **kwargs):
    if setting.startswith('SMART_ADMIN_'):
        attr = setting.replace('SMART_ADMIN_', '')
        globals()[attr] = value


def get_setting(entry):
    return globals()[entry]


get_setting_lazy = lazy(get_setting, str)
