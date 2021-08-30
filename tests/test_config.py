import pytest
from demo.urls import get_link

from smart_admin.settings import get_bookmarks, process_setting


@pytest.mark.parametrize("value", [10, lambda r: get_link.LINKS, 'demo.urls.get_link'])
def test_process_settings(value):
    assert process_setting(value, None)


@pytest.mark.parametrize("value", [get_link.LINKS, lambda r: get_link.LINKS, 'demo.urls.get_link'])
def test_bookmarks(value, settings):
    settings.SMART_ADMIN_BOOKMARKS = value
    assert get_bookmarks(None) == get_link.LINKS
