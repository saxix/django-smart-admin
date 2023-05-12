import pytest
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse


@pytest.mark.django_db
def test_content_type(app, settings):
    url = reverse(admin_urlname(ContentType._meta, 'changelist'))
    res = app.get(url, user='sax')
    assert res.status_code == 200


@pytest.mark.django_db
def test_content_type_stale(app, settings):
    url = reverse(admin_urlname(ContentType._meta, 'changelist'))
    res = app.get(url, user='sax')
    res = res.click("Check Stale")
    assert res.status_code == 200
