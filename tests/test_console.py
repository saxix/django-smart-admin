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


@pytest.mark.django_db
def test_email_panel(app, mailoutbox):
    url = reverse("admin:index")

    res = app.get(url, user='sax')
    res = res.click("Console")
    res = res.click("Test Email")
    res = res.form.submit()
    assert res.status_code == 200
    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == "Send email test: 'django.core.mail.send_mail'"


@pytest.mark.django_db
def test_migrations(app, mailoutbox):
    url = reverse("admin:index")
    res = app.get(url, user='sax')
    res = res.click("Console")
    res = res.click("Migrations")
    assert res.status_code == 200
