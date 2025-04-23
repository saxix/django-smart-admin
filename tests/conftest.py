import sys

import pytest
from django.urls import reverse


def pytest_configure(config):
    sys._called_from_pytest = True


@pytest.fixture
def app(django_app_factory):
    django_app = django_app_factory(csrf_checks=False)
    res = django_app.get(reverse("admin:login"))
    res.form["username"] = "sax"
    res.form["password"] = "123"
    res = res.form.submit()
    return django_app
