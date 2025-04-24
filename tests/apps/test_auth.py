from typing import TYPE_CHECKING

import pytest
from demo.factories import ContentTypeFactory, GroupFactory, UserFactory
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django_webtest import DjangoTestApp
from pyquery import PyQuery

from smart_admin.smart_auth.admin import User

if TYPE_CHECKING:
    from webtest import TestResponse

EXCLUDED_MODELS = ["Config", "StoredFilter"]


@pytest.mark.django_db
def test_user_btn_permissions(app: DjangoTestApp, settings):
    settings.SMART_LOGS_RETENTION_DAYS = 1
    g = GroupFactory(permissions=["add_user"])
    u = UserFactory(groups=[g], permissions=["delete_user"])
    url = reverse(admin_urlname(User._meta, "change"), args=[u.id])

    res: TestResponse = app.get(url, user="sax")
    res = res.click("Permissions", linkid="btn-permissions")
    assert PyQuery(res.text)("#permissions-list li:first-child a").text() == "auth.add_user"
    assert PyQuery(res.text)("#permissions-list li:nth-child(2) a").text() == "auth.delete_user"
    res = res.click("auth.add_user")
    assert res.status_code == 302


@pytest.mark.django_db
def test_user_add(app):
    url = reverse(admin_urlname(User._meta, "add"))
    res = app.get(url, user="sax")
    form = res.forms[1]
    form["username"] = "aaaa"
    form["password1"] = form["password2"] = "Super-Unsecure-Password"
    res = form.submit(name="_continue").follow()
    res = res.click("History")
    assert PyQuery(res.text)("#change-history tbody tr td:nth-child(3)").text() == "Added."


def test_user_history(app, settings):
    settings.SMART_LOGS_RETENTION_DAYS = 1
    g = GroupFactory()
    u = UserFactory(is_staff=True, is_active=True, is_superuser=True)
    url = reverse(admin_urlname(User._meta, "change"), args=[u.id])

    res = app.get(url, user="sax")
    form = res.forms[1]
    form["user_permissions"] = [Permission.objects.first().pk]
    form["groups"] = [g.pk]
    form.submit()

    res = app.get(url, user="sax")
    res = res.click("History")
    details = PyQuery(res.text)("#change-history tbody tr td:nth-child(4)").text()
    assert "Added permissions" in details
    assert "Added groups" in details


@pytest.mark.django_db
def test_permission_owners(app: DjangoTestApp, settings):
    settings.SMART_LOGS_RETENTION_DAYS = 1
    perm = Permission.objects.get(codename="add_user")

    g = GroupFactory(permissions=[perm])
    u = UserFactory(permissions=[perm])

    url = reverse(admin_urlname(Permission._meta, "change"), args=[perm.pk])
    res = app.get(url, user="sax")
    res = res.click("Users/Groups", linkid="btn-users")
    assert PyQuery(res.text)("#perms-users li:first-child a").text() == u.username
    assert PyQuery(res.text)("#perms-groups li:first-child a").text() == g.name


@pytest.mark.django_db
def test_contenttype_(app: DjangoTestApp, settings):
    ct = ContentTypeFactory(app_label="Stale", model="stale")
    url = reverse(admin_urlname(ContentType._meta, "changelist"))
    res = app.get(url, user="sax")
    res = res.click(linkid="check_stale")
    res = res.forms["cleanStaleForm"].submit().follow()
    assert PyQuery(res.text)("ul.messagelist").text() == "Removed 0 stale ContentTypes"

    res.forms["cleanStaleForm"]["ct"] = ct.pk
    res = res.forms["cleanStaleForm"].submit().follow()
    assert PyQuery(res.text)("ul.messagelist").text() == "Removed 1 stale ContentTypes"


@pytest.mark.django_db
def test_group_members(app: DjangoTestApp, settings):
    g = GroupFactory()
    u = UserFactory(groups=[g])
    url = reverse(admin_urlname(Group._meta, "change"), args=[g.id])
    res = app.get(url, user="sax")
    res = res.click(linkid="btn-members")
    assert PyQuery(res.text)("#group-members li:first-child a").text() == u.username


@pytest.mark.django_db
def test_group_add(app: DjangoTestApp, settings):
    url = reverse(admin_urlname(Group._meta, "add"))
    res = app.get(url, user="sax")
    res.forms["group_form"]["name"] = "New Group"
    res.forms["group_form"]["permissions"] = Permission.objects.filter(
        codename__in=["add_user", "delete_user"]
    ).values_list("pk", flat=True)
    res = res.forms["group_form"].submit(name="_continue").follow()
    res = res.click("History")
    details = PyQuery(res.text)("#change-history tbody tr:last-child td:nth-child(4)").text()
    assert "Permissions: add_user, delete_user" in details


def test_group_change(app: DjangoTestApp, settings):
    g = GroupFactory()
    url = reverse(admin_urlname(Group._meta, "change"), args=[g.id])
    res = app.get(url, user="sax")
    res.forms["group_form"]["name"] = "New Name"
    res = res.forms["group_form"].submit(name="_continue").follow()

    res.forms["group_form"]["permissions"] = Permission.objects.filter(
        codename__in=["add_user", "delete_user"]
    ).values_list("pk", flat=True)
    res = res.forms["group_form"].submit(name="_continue").follow()

    res = res.click("History")
    details = PyQuery(res.text)("#change-history tbody tr td:nth-child(4)").text()
    assert "Added permissions: add_user, delete_user" in details

    res = app.get(url, user="sax")
    res.forms["group_form"]["permissions"] = Permission.objects.filter(codename__in=["add_user"]).values_list(
        "pk", flat=True
    )
    res = res.forms["group_form"].submit(name="_continue").follow()
    res = res.click("History")
    details = PyQuery(res.text)("#change-history tbody tr:last-child td:nth-child(4)").text()
    assert "Removed permissions: delete_user" in details


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
