import logging

from django import forms
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class RedisCLIForm(forms.Form):
    command = forms.CharField()
    connection = forms.ChoiceField(choices=zip(settings.CACHES.keys(), settings.CACHES.keys()))


def panel_redis(self, request, extra_context=None):
    from django_redis import get_redis_connection
    from redis import ResponseError
    context = self.each_context(request)
    context["title"] = "Redis CLI"
    if request.method == "POST":
        form = RedisCLIForm(request.POST)
        if form.is_valid():
            r = get_redis_connection(form.cleaned_data["connection"])
            kwargs = r.get_connection_kwargs()
            context["redis"] = r
            context["connection_kwargs"] = kwargs
            try:
                stdout = r.execute_command(form.cleaned_data["command"])
                context["stdout"] = stdout
            except ResponseError as e:
                messages.add_message(request, messages.ERROR, str(e))
            except Exception as e:
                logger.exception(e)
                messages.add_message(request, messages.ERROR, f"{e.__class__.__name__}: {e}")
    else:
        form = RedisCLIForm()
    context["form"] = form
    return render(request, "smart_admin/panels/redis.html", context)


panel_redis.verbose_name = _("Redis CLI")
