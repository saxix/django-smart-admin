import re

from smart_admin.utils import MatchString, RegexString, SmartList


def test_smartlist():
    smart_list = SmartList(["abc", re.compile("x.."), RegexString("x.."), MatchString("1*")])
    assert "abc" in smart_list
    assert "xyz" in smart_list
    assert "123" in smart_list

    assert "ac" not in smart_list
    assert "xy" not in smart_list
