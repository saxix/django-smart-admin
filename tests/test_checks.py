from unittest import mock
from unittest.mock import Mock

from smart_admin.checks import check_bookmarks


def test_check_bookmarks():
    assert not check_bookmarks(Mock())


def test_check_bookmarks_error():
    with mock.patch("smart_admin.checks.get_bookmarks", side_effect=Exception):
        assert check_bookmarks(Mock())
