from unittest import mock

import pytest
from django.urls import reverse
from pyquery import PyQuery

from smart_admin.console.sentry import get_sentry_host, get_sentry_dashboard, get_event_url, make_sentry_link


def test_get_sentry_host(settings):
    settings.SENTRY_DSN = "https://abc.example.com/123"
    assert get_sentry_host() == "https://abc.example.com"

    settings.SENTRY_DSN = "https://abc.example.com:9000/123"
    assert get_sentry_host() == "https://abc.example.com:9000"


def test_get_sentry_dashboard(settings):
    settings.SENTRY_PROJECT = "PROJECT"
    assert get_sentry_dashboard() == "http://abc.example.com/PROJECT"

    del settings.SENTRY_PROJECT
    assert get_sentry_dashboard() == "N/A"

def test_get_event_url(settings):
    settings.SENTRY_DSN = "https://abc.example.com/123"
    settings.SENTRY_PROJECT = "PROJECT"
    assert get_event_url(123) == "https://abc.example.com/PROJECT/?query=123"
    del settings.SENTRY_PROJECT
    assert get_event_url(123) is None

def test_make_sentry_link(settings):
    settings.SENTRY_PROJECT = "PROJECT"
    assert make_sentry_link(123) == '<a href="http://abc.example.com/PROJECT/?query=123">123</a>'

    del settings.SENTRY_PROJECT
    assert make_sentry_link(123) == 123

    settings.SENTRY_PROJECT = "PROJECT"
    del settings.SENTRY_DSN
    assert make_sentry_link(123) == 123


@pytest.mark.django_db
@pytest.mark.parametrize("option", ["capture_event", "capture_exception", "capture_message",
                                    "logging_integration", "400", "403", "404", "500"])
def test_sentry_panel(app, option, settings):
    url = reverse("admin:console-sentry")
    res = app.post(url, {}, user="sax")
    assert res.status_code == 200

    with mock.patch("smart_admin.console.sentry.handler500"):
        res = app.get(url, user="sax")
        res.forms[1]["action"] = option
        res = res.forms[1].submit()
        assert PyQuery(res.text)("ul.messagelist").text() == "Sentry ID: None"

    #
    # res.forms[1]["action"] = "capture_event"
    # res = res.forms[1].submit()
    # assert PyQuery(res.text)("ul.messagelist").text() == "Sentry ID: None"
    #
    # res.forms[1]["action"] = "capture_exception"
    # res = res.forms[1].submit()
    # assert PyQuery(res.text)("ul.messagelist").text() == "Sentry ID: None"
    #
    # res.forms[1]["action"] = "capture_message"
    # res = res.forms[1].submit()
    # assert PyQuery(res.text)("ul.messagelist").text() == "Sentry ID: None"
    #
    # res.forms[1]["action"] = "logging_integration"
    # res = res.forms[1].submit()
    # assert PyQuery(res.text)("ul.messagelist").text() == "Sentry ID: None"
    #
    #
    # res.forms[1]["action"] = "400"
    # res = res.forms[1].submit()
    # assert PyQuery(res.text)("ul.messagelist").text() == "Sentry ID: None"
    #
    # res.forms[1]["action"] = "403"
    # res = res.forms[1].submit()
    # assert PyQuery(res.text)("ul.messagelist").text() == "Sentry ID: None"
    #
    # res.forms[1]["action"] = "404"
    # res = res.forms[1].submit()
    # assert PyQuery(res.text)("ul.messagelist").text() == "Sentry ID: None"

@pytest.mark.django_db
def test_sentry_panel_error(app, settings):
    url = reverse("admin:console-sentry")
    res = app.post(url, {}, user="sax")
    assert res.status_code == 200

    res = app.get(url, user="sax")

    # with mock.patch("smart_admin.console.sentry.handler500"):
    #     res.forms[1]["action"] = "500"
    #     res = res.forms[1].submit()
    #     assert PyQuery(res.text)("ul.messagelist").text() == "Sentry ID: None"

    del settings.SENTRY_DSN
    url = reverse("admin:console-sentry")
    res = app.get(url, user="sax").follow()
    assert PyQuery(res.text)("ul.messagelist").text() == "Sentry not configured. Please remove 'panel_sentry'."
