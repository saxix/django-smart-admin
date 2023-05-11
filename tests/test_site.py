import pytest
from django.urls import reverse

from demo.factories import ProductFactory


@pytest.mark.django_db
def test_autocomplete(app):
    url = reverse("admin:autocomplete")
    product=  ProductFactory(name="product1")
    res = app.get(f"{url}?app_label=demo&model_name=Product&field_name=name&term={product.name}", user='sax')

    assert res.json['results'][0]["text"]  == product.name
