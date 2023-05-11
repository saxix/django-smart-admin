from django.core.checks import Warning, register, Error
from django.http import HttpRequest
from django.apps import apps

from smart_admin.settings import get_bookmarks
from smart_admin.site import _parse_section


@register()
def check_bookmarks(app_configs, **kwargs):
    errors = []
    try:
        request = HttpRequest()
        get_bookmarks(request)
    except Exception as e:
        errors.append(
            Warning(
                'Unable to load SmartAdmin quick links',
                hint=str(e),
                obj='settings.SMART_ADMIN_BOOKMARKS',
                id='smart_admin.E001',
            )
        )
    return errors


@register()
def check_groups(app_configs, **kwargs):
    errors = []
    request = HttpRequest()
    sections = _parse_section()
    app_labels = [a.label for a in apps.app_configs.values()]
    for sect in sections:
        if sect in app_labels:
            errors.append(
                Error(
                    'Invalid SmartAdmin group name',
                    hint=f"'{sect}' clashes with ans application name",
                    obj='settings.SMART_ADMIN_SECTIONS',
                    id='smart_admin.E002',
                )
            )
    return errors
