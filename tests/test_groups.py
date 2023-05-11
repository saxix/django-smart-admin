import pytest
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from demo.factories import UserFactory, CustomerFactory, InvoiceFactory, GroupFactory
from demo.models import Customer


@pytest.mark.django_db
def test_content_type(app, settings):
    url = reverse(admin_urlname(Group._meta, 'changelist'))
    res = app.get(url, user='sax')
    assert res.status_code == 200

@pytest.mark.django_db
def test_content_type(app, settings):
    g = GroupFactory()
    url = reverse(admin_urlname(Group._meta, 'change'), args=[g.pk])
    res = app.get(url, user='sax')
    res = res.click("Members")
    assert res.status_code == 200
