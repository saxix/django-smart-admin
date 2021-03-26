#  :copyright: Copyright (c) 2018-2021. OS4D Ltd - All Rights Reserved
#  :license: Commercial
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Written by Stefano Apostolico <s.apostolico@gmail.com>, February 2021
import re
from fnmatch import fnmatch, fnmatchcase


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
