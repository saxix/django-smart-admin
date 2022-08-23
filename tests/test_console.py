import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_index(app):
    url = reverse("admin:index")

    res = app.get(url, user='sax')
    assert res.pyquery('a:contains("Smart Index")')
    res = res.click("Console")
    res = res.click("Migrations")
    res = res.click("System Info")
    assert res.status_code == 200
