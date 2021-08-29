import sys

import pytest
from django.urls import reverse


def pytest_configure(config):
    sys._called_from_pytest = True


@pytest.fixture(scope='function')
def app(django_app):
    res = django_app.get(reverse('admin:login'))
    res.form['username'] = 'sax'
    res.form['password'] = '123'
    res = res.form.submit()
    return django_app
