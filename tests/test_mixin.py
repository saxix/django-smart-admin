from django.contrib.auth.models import User
from unittest.mock import Mock

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
