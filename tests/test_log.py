import pytest
from demo.factories import LogEntryFactory, UserFactory
from django.contrib.admin.models import LogEntry
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.urls import reverse


@pytest.mark.django_db
def test_user_log(app, settings):
    settings.SMART_LOGS_RETENTION_DAYS = 1
    UserFactory(is_staff=True, is_active=True, is_superuser=True)
    url = reverse(admin_urlname(LogEntry._meta, 'changelist'))

    res = app.get(url, user='sax')
    assert res.status_code == 200


@pytest.mark.django_db
def test_user_truncate(app, settings):
    settings.SMART_LOGS_RETENTION_DAYS = 1
    url = reverse(admin_urlname(LogEntry._meta, 'truncate'))
    res = app.get(url, user='sax')
    res = res.form.submit()
    assert res.status_code == 302


@pytest.mark.django_db
def test_user_archive(app, settings):
    settings.SMART_LOGS_RETENTION_DAYS = 1
    url = reverse(admin_urlname(LogEntry._meta, 'archive'))
    res = app.get(url, user='sax')
    res = res.form.submit()
    assert res.status_code == 302


@pytest.mark.django_db
def test_user_edit_original(app, settings):
    settings.SMART_LOGS_RETENTION_DAYS = 1
    log_entry = LogEntryFactory()
    url = reverse(admin_urlname(LogEntry._meta, 'change'), args=[log_entry.id])
    res = app.get(url, user='sax')
    res = res.click("Edit Original")
    assert res.status_code == 200
