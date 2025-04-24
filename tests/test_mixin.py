from unittest.mock import Mock

from demo.factories import InvoiceFactory
from django.contrib.auth.models import User
from django.urls import reverse
from pyquery import PyQuery

from smart_admin.mixins import ReadOnlyMixin


def test_read_only_checks():
    o = ReadOnlyMixin(User(), Mock())
    assert [m.msg for m in o.check()] == []

    o.readonly_fields = None
    assert [m.msg for m in o.check()] == ["The value of 'readonly_fields' must be a list or tuple."]

    o.readonly_fields = ("__all__",)
    assert [m.msg for m in o.check()] == []

    o.readonly_fields = ()
    assert [m.msg for m in o.check()] == []

    o.readonly_fields = ("username",)
    assert [m.msg for m in o.check()] == []


def test_linked_objects(app):
    i = InvoiceFactory()
    url = reverse("admin:demo_customer_change", args=(i.customer.pk,))
    res = app.get(url, user="sax")
    res = res.click("Linked Objects")
    info = PyQuery(res.text)("#linked-objects table tbody tr:first-child")
    assert info("td:first-child a").text() == str(i.pk)
    assert info("td:nth-child(2)").text() == str(i)
