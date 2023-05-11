import json
import logging
import random
import threading
from inspect import getdoc, getmodule, signature
from typing import Protocol

import time

from celery.result import AsyncResult
from django.conf import settings
from django.core.cache import cache
from itertools import chain

from celery import current_app
from django import forms
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from celery.app.control import Inspect, Control

logger = logging.getLogger(__name__)


@current_app.task()
def test(*args, **kwargs):
    """ Dummy Task just for testing"""
    time.sleep(60)

#
# class CeleryActionForm(forms.Form):
#     ACTIONS = [
#         ("registered", _("Registered tasks")),
#         ("active_flat", _("Active tasks")),
#         ("scheduled", _("Scheduled tasks")),
#     ]
#
#     actions = forms.ChoiceField(label="Task actions", choices=ACTIONS, widget=forms.RadioSelect, required=False)
#
#     def execute(self, celery_app):
#         if self.errors:
#             raise ValueError("The action could not be executed because the data didn't validate.")
#
#         app_inspect = celery_app.control.inspect()
#
#         action = self.cleaned_data.get("actions")
#         if action == "active_flat":
#             active_tasks = app_inspect.active()
#             data = {task_info.pop("id"): task_info for task_info in list(chain(*active_tasks.values()))}
#         else:
#             data = getattr(app_inspect, action)()
#
#         return {dict(self.ACTIONS)[action]: data}
#
#     def _get_task_status(self, celery_app, task_id):
#         app_inspect = celery_app.control.inspect()
#         return app_inspect.query_task(task_id)
#
#
# def panel_celery_workers(request):
#     return {}


class Queue(Protocol):
    def len(self):
        ...


class RedisQueue:
    def len(self):
        from redis import from_url
        client = from_url(settings.CELERY_BROKER_URL)
        keys = client.keys("celery-task-meta*")
        return len(keys)

#
# class Runner(threading.Thread):
#     def __init__(self, monitor):
#         threading.Thread.__init__(self)
#         self.monitor = monitor
#
#     def run(self):
#         print("Running...")
#         with self.monitor.app.connection() as connection:
#             recv = self.monitor.app.events.Receiver(connection, handlers={
#                 'task-failed': self.monitor.handler,
#                 'task-received': self.monitor.handler,
#                 'task-rejected': self.monitor.handler,
#                 'task-retried': self.monitor.handler,
#                 'task-revoked': self.monitor.handler,
#                 'task-sent': self.monitor.handler,
#                 'task-started': self.monitor.handler,
#                 'task-succeeded': self.monitor.handler,
#                 # 'worker-online': self.monitor.handler,
#                 # 'worker-heartbeat': self.monitor.handler,
#                 # 'worker-offline': self.monitor.handler,
#             })
#             recv.capture(limit=None, timeout=None, wakeup=True)
#
#
# class Monitor:
#     def __init__(self, celery_app=None):
#         if celery_app is None:
#             from celery import current_app as celery_app
#
#         self.app = celery_app
#         self.state = self.app.events.State()
#         self.runner = Runner(monitor=self)
#         self.runner.start()
#
#     def handler(self, event):
#         self.state.event(event)
#         print("smart_admin/console/celery.py: 115", event)
#

class Celery:
    verbose_name = "Celery"
    url_name = 'panel_celery'
    cache_key = 'smart_celery_monitor'
    cache_ttl = 30

    def __init__(self):
        self.hooks = {}
        self.admin_site = None
    def add_hook(self, task_name, func):
        self.hooks[task_name] = func

    def inspect(self, task_name, task_info):
        try:
            print("smart_admin/console/celery.py: 137", task_info)
            if func := self.hooks.get(task_name, None):
                return func(task_name, task_info["args"], task_info["kwargs"])
            return {}
        except Exception as e:
            logger.exception(e)
            return {"error": str(e)}

    def get_celery_app(self):
        try:
            celery_app = self.admin_site.get_celery_app()
        except AttributeError:
            # Just a fallback is method is not defined, known as a bad practice
            from celery import current_app as celery_app
        return celery_app
    @cached_property
    def data(self):
        celery_app = self.get_celery_app()
        c: Control = celery_app.control
        i: Inspect = c.inspect()
        if (data := cache.get(self.cache_key, None)) is None:
            data = {"reserved": i.reserved() or {},
                    "registered": i.registered() or {},
                    "scheduled": i.scheduled() or {},
                    "active": i.active() or {},
                    "stats": i.stats() or {},
                    "registered_tasks": i.registered_tasks() or {}
                    }
            cache.set(self.cache_key, data, timeout=self.cache_ttl)
        return data

    def do_test(self, request, body):
        res: AsyncResult = test.delay(time.time(), a=random.randint(1, 100))
        return {"pid": res.id}

    def do_stats(self, request, body):
        return {"stats": self.data['stats']}

    def do_size(self, request, body):
        if getattr(settings, "CELERY_BROKER_URL") and settings.CELERY_BROKER_URL.startswith("redis"):
            backend = RedisQueue()
            return {"size": backend.len()}
        return {}

    def do_tasks(self, request, body):
        return {"tasks": self.data["registered_tasks"]}

    def do_worker(self, request, body):
        worker = body["name"]
        return {"reserved": self.data["reserved"].get(worker, []),
                "registered": self.data["registered"].get(worker, []),
                "scheduled": self.data["scheduled"].get(worker, []),
                "active": self.data["active"].get(worker, []),
                "worker": worker
                # **(i.stats() or {}).get(worker, {}),
                }

    def do_func(self, request, body):
        name = body["name"]
        try:
            if (response := cache.get(f"smart_celery_monitor:{name}", None)) is None:
                f = import_string(name)
                response = {"doc": getdoc(f) or "",
                            "module": str(getmodule(f) or ""),
                            "signature": str(signature(f)),
                            "func": name
                            }
                cache.set(f"smart_celery_monitor:{name}", response, timeout=3600)
            return response
        except Exception as e:
            logger.exception(e)
            return {"error": str(e)}

    def __call__(self, admin_site, request: HttpRequest, extra_context=None):
        # def panel_celery(self, request: HttpRequest, extra_context=None):
        self.admin_site = admin_site
        context = admin_site.each_context(request)
        context["title"] = "Celery"
        # if request.is_ajax():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            response = {}
            try:
                body = json.loads(request.body)
                method = getattr(self, f"do_{body['op']}")
                response = method(request, body)
                # if req["op"] == "test":
                #     res: AsyncResult = test.delay(time.time(), a=random.randint(1, 100))
                #     response = {"pid": res.id}
                # elif req["op"] == "terminate_all":
                #     terminated = []
                #     for worker_name, tasks in i.active().items():
                #         for info in tasks:
                #             terminated.append(info["id"])
                #             c.terminate(info["id"])
                #     response = {"terminated": terminated}
                # elif req["op"] == "purge":
                #     ret = c.purge()
                #     response = {"ret": ret}
                # elif req["op"] == "func":
                #     name = req["name"]
                #     try:
                #         if (response := cache.get(f"smart_celery_monitor:{name}", None)) is None:
                #             f = import_string(name)
                #             response = {"doc": getdoc(f) or "",
                #                         "module": str(getmodule(f) or ""),
                #                         "signature": str(signature(f)),
                #                         }
                #             cache.set(f"smart_celery_monitor:{name}", response, timeout=3600)
                #
                #     except Exception as e:
                #         logger.exception(e)
                #         response = {"error": str(e)}
                # elif req["op"] == "queue":
                #     backend = RedisQueue()
                #     response = {"size": backend.len()}
                # elif req["op"] == "stats":
                #     response = {"stats": i.stats()}
                # elif req["op"] == "task":
                #     info = i.query_task(req["id"])
                #     details = list(list(info.items())[0][1].items())[0][1][1]
                #     response = {"info": details,
                #                 "extra": self.inspect(details["name"], details)
                #                 }
                # elif req["op"] == "tasks":
                #     response = {"tasks": i.registered_tasks()}
                # elif req["op"] == "worker":
                #     worker = req["name"]
                #     response = {"reserved": data["reserved"].get(worker, []),
                #                 "registered": data["registered"].get(worker, []),
                #                 "scheduled": data["scheduled"].get(worker, []),
                #                 "active": data["active"].get(worker, []),
                #                 # **(i.stats() or {}).get(worker, {}),
                #                 }
            except Exception as e:
                print("smart_admin/console/celery.py: 259", e)
                logger.exception(e)
            return JsonResponse(response)

        return render(request, "smart_admin/panels/celery.html", context)


panel_celery = Celery()
