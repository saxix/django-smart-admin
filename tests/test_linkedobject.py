import pytest
from demo.factories import InvoiceFactory, UserFactory
from demo.models import Customer
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.urls import reverse


@pytest.mark.django_db
def test_linked_objects(app, settings):
    UserFactory(is_staff=True, is_active=True, is_superuser=True)
    invoice = InvoiceFactory()
    url = reverse(admin_urlname(Customer._meta, 'change'), args=[invoice.customer_id])
    res = app.get(url, user='sax')
    res = res.click("Linked Objects")
    assert res.status_code == 200
