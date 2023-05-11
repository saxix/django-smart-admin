import pytest
import sentry_sdk
from django.urls import reverse


@pytest.mark.django_db
def test_panel(app, mailoutbox, settings):
    settings.SENTRY_DSN = "http://sentry"
    settings.SENTRY_PROJECT = "smart-admin"
    url = reverse("admin:index")
    res = app.get(url, user='sax')
    res = res.click("Console")
    res = res.click("Sentry")
    assert res.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize("action", ["capture_event", "capture_exception", "capture_message",
                                    "logging_integration", "400", "403", "404", "500"])
def test_panel_sentry(app, action, settings, monkeypatch):
    monkeypatch.setattr(sentry_sdk, "last_event_id", lambda: 1)
    settings.SENTRY_DSN = "http://sentry:443"
    settings.SENTRY_PROJECT = "smart-admin"
    url = reverse("admin:sentry")
    res = app.get(url, user='sax')
    res.form["action"] = action
    res = res.form.submit()
    assert res.status_code == 200


@pytest.mark.django_db
def test_panel_fail(app, settings):
    settings.SENTRY_DSN = "http://sentry:443"
    url = reverse("admin:sentry")
    res = app.get(url, user='sax')
    res = res.form.submit()
    assert res.status_code == 200
