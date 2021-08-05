import pytest
from django.contrib.admin.models import LogEntry
from django.contrib.admin.sites import site

from demo.factories import get_factory_for_model
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db.models.options import Options
from django.urls import reverse

EXCLUDED_MODELS = ['Config']


def pytest_generate_tests(metafunc):
    if 'modeladmin' in metafunc.fixturenames:
        m = []
        ids = []
        for model, admin in site._registry.items():
            if model.__name__ not in EXCLUDED_MODELS:
                m.append(admin)
                ids.append(admin.__class__.__name__)
        metafunc.parametrize("modeladmin", m, ids=ids)


@pytest.fixture()
def record(db, request):
    # TIPS: database access is forbidden in pytest_generate_tests
    modeladmin = request.getfixturevalue('modeladmin')
    factory = get_factory_for_model(modeladmin.model)
    return factory()


@pytest.mark.django_db
def test_index(app):
    url = reverse("admin:index")

    res = app.get(url, user='sax')
    assert res.pyquery('a:contains("Smart Index")')

    app.set_cookie('smart', "1")
    res = app.get(reverse("admin:index"), user='sax')
    assert res.pyquery('a:contains("Standard Index")')


@pytest.mark.django_db
def test_applist(app):
    url = reverse("admin:index")

    res = app.get(url, user='sax')
    assert res.pyquery('a:contains("Smart Index")')

    app.set_cookie('smart', "1")
    res = app.get(url, user='sax')
    assert res.pyquery('a:contains("Standard Index")')


@pytest.mark.django_db
def test_group_list(app):
    url = reverse("admin:group_list", args=["Security"])

    res = app.get(url, user='sax')
    assert res.pyquery('a:contains("Smart Index")')

    app.set_cookie('smart', "1")
    res = app.get(url, user='sax')
    assert res.pyquery('a:contains("Standard Index")')


@pytest.mark.django_db
def test_changelist(app, modeladmin, record):
    url = reverse(admin_urlname(modeladmin.model._meta, 'changelist'))
    opts: Options = modeladmin.model._meta

    res = app.get(url, user='sax')
    assert str(opts.app_config.verbose_name) in str(res.content)
    assert res.pyquery('a:contains("Smart Index")')

    app.set_cookie('smart', "1")
    res = app.get(url, user='sax')
    assert res.pyquery('a:contains("Standard Index")')


@pytest.mark.django_db
def test_changeform(app, modeladmin, record):
    url = reverse(admin_urlname(modeladmin.model._meta, 'change'), args=[record.id])
    opts: Options = modeladmin.model._meta

    res = app.get(url, user='sax')
    assert str(opts.app_config.verbose_name) in str(res.content)
    assert res.pyquery('a:contains("Smart Index")')

    app.set_cookie('smart', "1")
    res = app.get(url, user='sax')
    assert res.pyquery('a:contains("Standard Index")')


@pytest.mark.django_db
def test_log(app):
    url = reverse(admin_urlname(LogEntry._meta, 'changelist'))
    opts: Options = LogEntry._meta

    res = app.get(url, user='sax')
    assert str(opts.app_config.verbose_name) in str(res.content)
    assert res.pyquery('a:contains("Smart Index")')

    app.set_cookie('smart', "1")
    res = app.get(url, user='sax')
    assert res.pyquery('a:contains("Standard Index")')
