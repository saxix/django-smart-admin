import datetime
from typing import TYPE_CHECKING
from unittest import mock

import pytest
from demo.factories import LogEntryFactory
from django.contrib.admin.models import LogEntry
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db import OperationalError
from django.urls import reverse
from pyquery import PyQuery

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


@pytest.mark.django_db(transaction=True)
def test_truncate_log(app, settings):
    url = reverse(admin_urlname(LogEntry._meta, "changelist"))
    LogEntryFactory()
    res = app.get(url, user="sax")
    res = res.click("Truncate")
    form = res.forms["truncate-form"]
    res = form.submit().follow()
    assert PyQuery(res.text)("ul.messagelist").text() == "Table truncated"


@pytest.mark.django_db(transaction=True)
def test_truncate_log_fallback(app, settings):
    url = reverse(admin_urlname(LogEntry._meta, "changelist"))
    res = app.get(url, user="sax")
    res = res.click("Truncate")
    with mock.patch("smart_admin.mixins.truncate_model_table", side_effect=OperationalError):
        form = res.forms["truncate-form"]
        res = form.submit().follow()
        assert PyQuery(res.text)("ul.messagelist").text() == "Truncate failed."
