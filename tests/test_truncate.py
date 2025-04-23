import pytest
from demo.factories import CustomerFactory
from demo.models import Customer

from smart_admin.truncate import TruncateMixin, truncate_model_table


@pytest.mark.django_db(transaction=True)
def test_truncate():
    c = CustomerFactory()
    truncate_model_table(Customer, True)
    c = CustomerFactory()
    assert c.pk == 1
    truncate_model_table(Customer, False)
    c = CustomerFactory()
    assert c.pk == 2


@pytest.mark.django_db(transaction=True)
def test_truncate_mixin():
    m = TruncateMixin()
    m.model = Customer
    m.truncate()
