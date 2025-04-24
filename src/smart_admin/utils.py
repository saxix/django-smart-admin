import re
from fnmatch import fnmatchcase

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import OneToOneRel


def as_bool(value):
    return value not in ["", "0", "None", 0, None, "on"]


class MatchString(str):
    def __repr__(self):
        return f"m[{self}]"


class RegexString(str):
    def __init__(self, pattern, options=0):
        self._rex = re.compile(pattern, options)

    def __repr__(self):
        return f"r[{self._rex.pattern}]"


class SmartList(list):
    def __contains__(self, target: str):
        t = str(target)
        for entry in self:
            if isinstance(entry, MatchString):
                if fnmatchcase(t, entry):
                    return True
            elif isinstance(entry, re.Pattern):
                m = entry.match(t)
                if m and m.group():
                    return bool(m)
            elif isinstance(entry, RegexString):
                m = entry._rex.match(t)
                if m and m.group():
                    return bool(m)
            elif entry == target:
                return True
        return False


def get_linked_objects(
    original: models.Model,
    ignored: list[str] | None = None,
    selection: list[str] | None = None,
    max_records=200,
    include_empty: bool = False,
) -> tuple[list, list]:
    ignored = ignored or []
    selection = selection or [f for f in original._meta.get_fields() if f.auto_created and not f.concrete]
    filtered = [x for x in selection if (x not in ignored)]
    linked = []
    empty = []
    for f in filtered:
        info = get_related(original, f, max_records=max_records)
        if info["count"] == 0:
            if include_empty:
                empty.append(info)
        else:
            linked.append(info)
    return linked, empty


def get_related(user, field, max_records=200):
    info = {
        "owner": user,
        "to": field.model._meta.model_name,
        "field_name": field.name,
        "count": 0,
        "link": admin_urlbasename(field.related_model._meta, "changelist"),
        "filter": "",
        "data": [],
    }
    try:
        info["related_name"] = field.related_model._meta.verbose_name
        if field.related_name:
            related_attr = getattr(user, field.related_name)
        elif isinstance(field, OneToOneRel):
            related_attr = getattr(user, field.name)
        else:
            related_attr = getattr(user, f"{field.name}_set", None)
        if related_attr:
            info["filter"] = f"{field.field.name}={user.pk}"

            if hasattr(related_attr, "all") and callable(related_attr.all):
                related = related_attr.all()[: max_records or 200]
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


def admin_site_urlname(admin_site, value, arg):
    return "%s:%s_%s_%s" % (admin_site.name, value.app_label, value.model_name, arg)


def admin_urlbasename(value, arg):
    return "%s_%s_%s" % (value.app_label, value.model_name, arg)
