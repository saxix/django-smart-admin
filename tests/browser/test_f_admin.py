import pytest
from demo.selenium import TestBrowser
from django.urls import reverse

pytestmark = pytest.mark.functional


def test_console_index(browser: TestBrowser):
    browser.login()
    browser.open(reverse("admin:index"))
    browser.open(reverse("admin:console"))


def test_console_migrations(browser: TestBrowser):
    browser.login()
    browser.open(reverse("admin:console"))

    browser.click_link_text("Migrations")
    browser.click_link_text("LIST")
    browser.click_link_text("PLAN")


def test_console_sysinfo(browser: TestBrowser):
    browser.login()
    browser.open(reverse("admin:console"))

    browser.click_link_text("System Info")
    browser.type("#filterInput", "database")


def test_console_sentry(browser: TestBrowser):
    browser.login()
    browser.open(reverse("admin:console"))

    browser.click_link_text("Sentry")
    browser.click("input[type=radio][value='capture_event']")
    browser.click("input[type=submit][value='Execute']")
    assert browser.get_text("ul.messagelist") == "Sentry ID: None"


def test_user_permissions(browser: TestBrowser):
    browser.login()
    browser.open(reverse("admin:auth_user_changelist"))
    browser.click_link_text(browser.admin_user.username)
    browser.click("#btn-permissions")
    browser.click_link_text(browser.admin_user.username)
