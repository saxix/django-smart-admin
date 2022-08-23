import re
from fnmatch import fnmatchcase

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.exceptions import ObjectDoesNotExist


def as_bool(value):
    return value not in ["", "0", "None", 0, None, "on"]


class match(str):
    def __repr__(self):
        return f'm[{self}]'


class regex(str):
    def __init__(self, pattern, options=0):
        self._rex = re.compile(pattern, options)

    def __repr__(self):
        return f'r[{self._rex.pattern}]'

    def __str__(self):
        return self._rex.pattern


class SmartList(list):
    def __contains__(self, target):
        t = str(target)
        for entry in self:
            if isinstance(entry, match):
                if fnmatchcase(target, entry):
                    return True
            elif isinstance(entry, re.Pattern):
                m = entry.match(t)
                if m and m.group():
                    return bool(m)
            elif isinstance(entry, regex):
                m = entry._rex.match(t)
                if m and m.group():
                    return bool(m)
            elif entry == target:
                return True
        return False


def get_related(user, field, max_records=200):
    info = {
        "owner": user,
        "to": field.model._meta.model_name,
        "field_name": field.name,
        "count": 0,
        "link": admin_urlname(field.related_model._meta, "changelist"),
        "filter": "",
    }
    try:
        info["related_name"] = field.related_model._meta.verbose_name
        if field.related_name:
            related_attr = getattr(user, field.related_name)
        else:
            related_attr = getattr(user, f"{field.name}_set")
        info["filter"] = f"{field.field.name}={user.pk}"

        if hasattr(related_attr, 'all') and callable(related_attr.all):
            related = related_attr.all()[:max_records or 200]
            count = related_attr.all().count()
        else:
            related = [related_attr]
            count = 1
        info["data"] = related
        info["count"] = count
    except ObjectDoesNotExist:
        info["data"] = []
        info["related_name"] = field.related_model._meta.verbose_name

    return info


def masker(value, request):
    if request.user.is_superuser:
        return value
    return "****"
