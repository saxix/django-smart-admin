import re
from collections import namedtuple
from fnmatch import fnmatchcase
from . import settings as smart_settings

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


def get_related(user, field):
    info = {
        "to": field.model._meta.model_name,
        "field_name": field.name,
    }

    try:
        info["related_name"] = field.related_model._meta.verbose_name
        if field.related_name:
            related_attr = getattr(user, field.related_name)
        else:
            related_attr = getattr(user, f"{field.name}_set")

        if hasattr(related_attr, 'all') and callable(related_attr.all):
            related = related_attr.all()
            opts = related_attr.model._meta
            # info["related_name"] = opts.verbose_name
        else:
            opts = related_attr._meta
            related = [related_attr]
            # info["related_name"] = opts.verbose_name
        info["data"] = related
    except ObjectDoesNotExist:
        info["data"] = []
        info["related_name"] = field.related_model._meta.verbose_name

    return info

#
# Link = namedtuple('Link', "label,href,css_class")
# Sep = namedtuple('Sep', "css_class")

def get_bookmarks2(request):
    return smart_settings.get_bookmarks(request)
    # if smart_settings.BOOKMARKS_PERMISSION is None or request.user.has_permission(
    #         smart_settings.BOOKMARKS_PERMISSION):
    #     bookmarks = []
    #     values = smart_settings.get_bookmarks(request)
    #     for defs in values:
    #         if not defs:
    #             continue
    #         if isinstance(defs, (Link, Sep)):
    #             entry = defs
    #         elif isinstance(defs, str):
    #             entry = defs
    #         elif isinstance(defs, (list, tuple)) and len(defs) == 2:
    #             entry = Link(defs[0], defs[1], 'viewlink')
    #         elif isinstance(defs, (list, tuple)) and len(defs) == 3:
    #             entry = Link(defs)
    #         else:
    #             raise ValueError(f"Invalid QuickLink definition '{defs}' for BOOKMARKS")
    #         bookmarks.append(entry)
    #     return bookmarks
    # return []
