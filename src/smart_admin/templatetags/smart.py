import json
import urllib.parse

from django import template
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from smart_admin.utils import as_bool

register = template.Library()


@register.filter()
def section(model_to_section, opts):
    return model_to_section[f"{opts.app_label}.{opts.object_name}"]


@register.simple_tag(takes_context=True)
def smart_toggler(context):
    request = context['request']
    page = urllib.parse.quote(request.path)
    if as_bool(request.COOKIES.get('smart', "0")):
        label = _("Standard Index")
        t = "on"
    else:
        label = _("Smart Index")
        t = "off"

    toggler = reverse("admin:smart_toggle", args=[t])
    return mark_safe(f'<a href="{toggler}?from={page}">{label}</a>')


@register.simple_tag()
def get_changed(message, entry):
    try:
        change_message = json.loads(message)
        # if isinstance(change_message, (list, tuple)) and change_message:
        #     if 'changed' in change_message[0] and 'permissions' in change_message[0]['changed']:
        return change_message[0]['changed'][entry]
    except (json.JSONDecodeError, KeyError, IndexError):
        pass
    return ""


@register.filter()
def get_admin_link(record):
    opts = record._meta
    url_name = admin_urlname(opts, "change")
    return reverse(url_name, args=[record.pk])


@register.simple_tag()
def get_admin_href(record, field=None):
    opts = record._meta
    url_name = admin_urlname(opts, "change")
    if field:
        label = getattr(record, field)
    else:
        label = str(record)
    try:
        url = reverse(url_name, args=[record.pk])
        tag = f'<a href="{url}">{label}</a>'
    except NoReverseMatch:
        tag = label
    return mark_safe(tag)
