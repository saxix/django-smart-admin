import datetime

import pytest
from demo.factories import GroupFactory, LogEntryFactory, UserFactory, get_factory_for_model
from django.contrib.admin.models import LogEntry
from django.contrib.admin.sites import site
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.auth.models import Group, Permission
from django.db.models.options import Options
from django.urls import reverse

from smart_admin.smart_auth.admin import User

EXCLUDED_MODELS = ['Config', 'StoredFilter']


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
    try:
        return factory()
    except Exception as e:
        raise Exception(f"Error creating fixture for {modeladmin.model}") from e


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


@pytest.mark.django_db
def test_archive_log(app, settings):
    settings.SMART_LOGS_RETENTION_DAYS = 1
    url = reverse(admin_urlname(LogEntry._meta, 'changelist'))
    LogEntryFactory()
    LogEntryFactory(action_time=datetime.date(2000, 1, 1))
    res = app.get(url, user='sax')
    res = res.click("Archive")
    res = res.form.submit()
    assert res.status_code == 302
    assert LogEntry.objects.count() == 1


@pytest.mark.django_db
def test_group_history(app, settings):
    settings.SMART_LOGS_RETENTION_DAYS = 1
    g = GroupFactory()
    url = reverse(admin_urlname(Group._meta, 'change'), args=[g.id])
    res = app.get(url, user='sax')
    res.form['permissions'] = [Permission.objects.first().pk]
    res.form.submit()

    res = app.get(url, user='sax')
    res = res.click("History")
    assert "Added permissions" in res.content.decode()


@pytest.mark.django_db
def test_user_history(app, settings):
    settings.SMART_LOGS_RETENTION_DAYS = 1
    g = GroupFactory()
    u = UserFactory(is_staff=True, is_active=True, is_superuser=True)
    url = reverse(admin_urlname(User._meta, 'change'), args=[u.id])

    res = app.get(url, user='sax')
    res.form['user_permissions'] = [Permission.objects.first().pk]
    res.form['groups'] = [g.pk]
    res.form.submit()

    res = app.get(url, user='sax')
    res = res.click("History")
    assert "Added permissions" in res.content.decode()
    assert "Added groups" in res.content.decode()
