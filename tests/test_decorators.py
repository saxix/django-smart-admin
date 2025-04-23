from contextlib import nullcontext as does_not_raise
import pytest

from demo.admin import CustomerAdmin
from demo.models import Customer
from smart_admin.decorators import smart_register
from django.contrib.admin.sites import site as default_site


@pytest.mark.parametrize(
    "models, model_admin, site, expectation",
    [
        ([], None, None, pytest.raises(ValueError, match="At least one model must be passed to register.")),
        ([None], None, object, pytest.raises(ValueError, match="site must subclass AdminSite")),
        ([object], object, default_site, pytest.raises(ValueError, match="Wrapped class must subclass ModelAdmin.")),
        ([Customer], CustomerAdmin, default_site, does_not_raise()),
    ],
)
def test_smart_register_exceptions(models, model_admin, site, expectation):
    with expectation:
        smart_register(*models, site=site)(model_admin)
