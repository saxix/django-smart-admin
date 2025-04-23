import sys

import pytest
from demo.factories import SuperUserFactory
from django.urls import reverse


def pytest_configure(config):
    sys._called_from_pytest = True


@pytest.fixture
def app(db, django_app_factory):
    u = SuperUserFactory(username="sax")
    django_app = django_app_factory(csrf_checks=False)
    res = django_app.get(reverse("admin:login"))
    res.form["username"] = u.username
    res.form["password"] = u._password
    res = res.form.submit()
    return django_app
