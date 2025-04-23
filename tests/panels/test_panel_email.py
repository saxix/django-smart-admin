import pytest
from django.urls import reverse
from unittest import mock

from pyquery import PyQuery


@pytest.mark.django_db
def test_email_panel(app, mailoutbox):
    url = reverse("admin:index")

    res = app.get(url, user="sax")
    res = res.click("Console")
    res = res.click("Test Email")
    res = res.forms[1].submit()
    assert res.status_code == 200
    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == "Send email test: 'django.core.mail.send_mail'"

@pytest.mark.django_db
def test_email_panel_none_sent(app, mailoutbox):
    url = reverse("admin:console-email")
    res = app.get(url, user="sax")

    with mock.patch("django.core.mail.send_mail", return_value=0):
        res = res.forms[1].submit()
        assert res.status_code == 200
        assert len(mailoutbox) == 0
        assert PyQuery(res.text)("ul.messagelist").text() == "No errors raised but no messages sent to sax@demo.org"


@pytest.mark.django_db
def test_email_panel_error(app, mailoutbox):
    url = reverse("admin:console-email")
    res = app.get(url, user="sax")
    with mock.patch("django.core.mail.send_mail", side_effect=Exception):
        res = res.forms[1].submit()
        assert res.status_code == 200
        assert len(mailoutbox) == 0
        assert PyQuery(res.text)("ul.messagelist").text() == "Error sending email."



@pytest.mark.django_db
def test_email_panel_conn_failure(app, mailoutbox):
    url = reverse("admin:console-email")
    res = app.get(url, user="sax")
    with mock.patch("django.core.mail.get_connection", side_effect=Exception):
        res = res.forms[1].submit()
        assert res.status_code == 200
        assert len(mailoutbox) == 0
        assert PyQuery(res.text)("ul.messagelist").text() == "Error sending email."
