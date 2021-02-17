import urllib.parse

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

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
        label = "Standard Index"
        t = "on"
    else:
        label = "Smart Index"
        t = "off"

    toggler = reverse("admin:smart_toggle", args=[t])
    return mark_safe(f'<a href="{toggler}?from={page}">{label}</a>')
