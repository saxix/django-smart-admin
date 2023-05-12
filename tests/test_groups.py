import pytest
from demo.factories import GroupFactory
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.auth.models import Group
from django.urls import reverse


@pytest.mark.django_db
def test_groups(app, settings):
    url = reverse(admin_urlname(Group._meta, 'changelist'))
    res = app.get(url, user='sax')
    assert res.status_code == 200


@pytest.mark.django_db
def test_group_member(app, settings):
    g = GroupFactory()
    url = reverse(admin_urlname(Group._meta, 'change'), args=[g.pk])
    res = app.get(url, user='sax')
    res = res.click("Members")
    assert res.status_code == 200
