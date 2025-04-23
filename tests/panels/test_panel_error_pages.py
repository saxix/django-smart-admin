from unittest import mock

import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize("option", ["400", "403", "404", "500"])
def test_error_pages(app, option, settings):
    url = reverse("admin:console-error_page")

    with mock.patch("smart_admin.console.sentry.handler500"):
        res = app.get(url, user="sax", expect_errors=True)
        res.forms[1]["action"] = option
        res = res.forms[1].submit(expect_errors=True)
