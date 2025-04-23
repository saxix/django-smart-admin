import builtins
from unittest.mock import Mock

import pytest
from django.urls import reverse
from pyquery import PyQuery
from redis import ResponseError


class MockedRedis:
    def __init__(self, exc: Exception = None):
        self.exc = exc

    def get_connection_kwargs(self):
        return {}

    def execute_command(self, cmd: str) -> list[str]:
        if self.exc:
            raise self.exc
        return [f"Output for {cmd}"]


@pytest.fixture
def fail_redis():
    def myimport(name, globals_, locals_, fromlist, level):
        if "django_redis" in name:
            raise ModuleNotFoundError("No module named 'django_redis'")
        return realimport(name, globals_, locals_, fromlist, level)

    realimport = builtins.__import__
    builtins.__import__ = myimport
    yield
    builtins.__import__ = realimport


@pytest.mark.django_db
def test_redis_missing(app, fail_redis):
    url = reverse("admin:console-panel_redis")

    res = app.get(url).follow()
    assert res.status_code == 200
    assert (
        PyQuery(res.text)("ul.messagelist").text()
        == "ModuleNotFoundError: No module named 'django_redis'. Please remove `panel_redis`"
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "exc, message", [(None, None), (ResponseError("R-error"), "R-error"), (Exception("E-error"), "Exception: E-error")]
)
def test_redis_command(app, exc, message, monkeypatch):
    url = reverse("admin:console-panel_redis")

    res = app.get(url)
    res.forms[1]["command"] = "dummy_command"

    monkeypatch.setattr("django_redis.get_redis_connection", Mock(return_value=MockedRedis(exc)))
    res = res.forms[1].submit()
    if message:
        assert PyQuery(res.text)("ul.messagelist").text() == message
    else:
        assert PyQuery(res.text)("pre.code").text() == "1) Output for dummy_command"
