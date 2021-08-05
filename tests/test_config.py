import pytest
from smart_admin.settings import process_lazy
from demo.urls import get_link


@pytest.mark.parametrize("value", [get_link.LINKS, lambda r: get_link.LINKS, 'demo.urls.get_link'])
def test_bookmarks(value, settings):
    settings.SMART_ADMIN_BOOKMARKS = value
    assert process_lazy('BOOKMARKS') == get_link.LINKS
