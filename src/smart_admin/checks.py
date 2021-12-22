from django.core.checks import Warning, register
from django.http import HttpRequest

from smart_admin.settings import get_bookmarks


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
