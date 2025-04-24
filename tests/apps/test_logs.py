import datetime
from typing import TYPE_CHECKING

import pytest
from demo.factories import GroupFactory, LogEntryFactory
from django.contrib.admin.models import LogEntry
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

if TYPE_CHECKING:
    from django.db.models.options import Options

EXCLUDED_MODELS = ["Config", "StoredFilter"]


@pytest.mark.django_db
def test_log(app):
    url = reverse(admin_urlname(LogEntry._meta, "changelist"))
    opts: Options = LogEntry._meta

    res = app.get(url, user="sax")
    assert str(opts.app_config.verbose_name) in str(res.content)
    assert res.pyquery('a:contains("Smart Index")')

    app.set_cookie("smart", "1")
    res = app.get(url, user="sax")
    assert res.pyquery('a:contains("Standard Index")')


@pytest.mark.django_db
def test_archive_log(app, settings):
    settings.SMART_LOGS_RETENTION_DAYS = 1
    url = reverse(admin_urlname(LogEntry._meta, "changelist"))
    LogEntryFactory()
    LogEntryFactory(action_time=datetime.date(2000, 1, 1))
    res = app.get(url, user="sax")
    res = res.click("Archive")
    form = res.forms[1]
    res = form.submit()
    assert res.status_code == 302
    assert LogEntry.objects.count() == 1


@pytest.mark.django_db
def test_group_history(app, settings):
    settings.SMART_LOGS_RETENTION_DAYS = 1
    g = GroupFactory()
    url = reverse(admin_urlname(Group._meta, "change"), args=[g.id])
    res = app.get(url, user="sax")
    form = res.forms[1]
    form["permissions"] = [Permission.objects.first().pk]
    res = form.submit()

    res = app.get(url, user="sax")
    res = res.click("History")
    assert "Added permissions" in res.content.decode()
