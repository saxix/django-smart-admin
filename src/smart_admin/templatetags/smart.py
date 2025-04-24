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
    request = context["request"]
    page = urllib.parse.quote(request.path)
    if as_bool(request.COOKIES.get("smart", "0")):
        label = _("Standard Index")
        t = "on"
    else:
        label = _("Smart Index")
        t = "off"

    toggler = reverse("admin:smart_toggle", args=[t])
    return mark_safe(f'<a href="{toggler}?from={page}">{label}</a>')  # noqa: S308


@register.simple_tag()
def get_message_details(message):
    try:
        messages = json.loads(message)
        return messages[0]
    except (json.JSONDecodeError, KeyError, IndexError):
        pass
    return ""


@register.filter()
def get_admin_link(record):
    opts = record._meta
    url_name = admin_urlname(opts, "change")
    return reverse(url_name, args=[record.pk])


@register.simple_tag(takes_context=True)
def get_admin_href(context, record, field=None):
    admin_site = context["admin_site"]
    if field:
        label = getattr(record, field)
    else:
        label = str(record)
    try:
        url = admin_site.reverse_object_url(record, "change")
        tag = f'<a href="{url}">{label}</a>'
    except NoReverseMatch:
        tag = label
    return mark_safe(tag)  # noqa: S308


@register.simple_tag(takes_context=True)
def get_admin_url_name(context, app_label, model_name, page, opts=None):
    admin_site = context["admin_site"]
    return "%s:%s_%s_%s" % (admin_site.name, app_label, model_name, page)
