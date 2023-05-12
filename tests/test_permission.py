import pytest
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.auth.models import Permission
from django.urls import reverse


@pytest.mark.django_db
def test_permission(app, settings):
    url = reverse(admin_urlname(Permission._meta, 'changelist'))
    res = app.get(url, user='sax')
    assert res.status_code == 200


@pytest.mark.django_db
def test_permission_owners(app, settings):
    url = reverse(admin_urlname(Permission._meta, 'change'), args=[Permission.objects.first().pk])
    res = app.get(url, user='sax')
    res = res.click("Users/Groups")
    assert res.status_code == 200
