from django import template

register = template.Library()


@register.filter()
def section(model_to_section, opts):
    return model_to_section[f"{opts.app_label}.{opts.object_name}"]


@register.filter(name="bool")
def as_bool(value):
    return value not in ["", "0", "None", 0, None]
