from unittest.mock import Mock

import pytest
from django.urls import reverse

from smart_admin.console import panel_celery
from smart_admin.console.celery import RedisQueue


class CeleryApp:
    def __init__(self):
        inspect = Mock(reserved=lambda: {"worker1": ["task-1"]},
                       registered=lambda: {"worker1": ["task-1", "task-2"]},
                       scheduled=lambda: {"worker1": ["task-1"]},
                       active=lambda: {"worker1": ["task-1"]},
                       stats=lambda: {"worker1": ["task-1"]},
                       registered_tasks=lambda: ["task-1", "task-2", "task-3"],
                       )
        self.control = Mock(inspect=lambda: inspect)


@pytest.mark.django_db
def test_panel(app, monkeypatch):
    monkeypatch.setattr(panel_celery, 'get_celery_app', lambda: CeleryApp())
    url = reverse("admin:index")
    res = app.get(url, user='sax')
    res = res.click("Console")
    res = res.click("Celery")
    assert res.status_code == 200


DATA = [
    # {"op": "test"},
    {"op": "tasks"},
    {"op": "stats"},
    {"op": "size"},
    {"op": "func", "name": "smart_admin.console.celery.test"},
    {"op": "worker", "name": "worker1"},
]


@pytest.mark.django_db
@pytest.mark.parametrize("action", DATA, ids=[e["op"] for e in DATA])
def test_panel_run(app, action, monkeypatch, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_BROKER_URL = "redis://redisserver"
    monkeypatch.setattr(RedisQueue, 'len', Mock(return_value=10))
    monkeypatch.setattr(panel_celery, 'get_celery_app', lambda: CeleryApp())

    url = reverse("admin:panel_celery")
    res = app.get(url, user='sax')
    token = res.pyquery('#celery').attr('data-token')
    res = app.post_json(url, action, user='sax', headers={"x-requested-with": 'XMLHttpRequest',
                                                          "X-CSRFToken": token
                                                          })
    assert res.json[action["op"]]
    assert res.status_code == 200
