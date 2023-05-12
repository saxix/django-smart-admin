import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_panel(app, mailoutbox):
    url = reverse("admin:index")
    res = app.get(url, user='sax')
    res = res.click("Console")
    res = res.click("Migrations")
    assert res.status_code == 200
