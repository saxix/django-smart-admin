import logging
from urllib.parse import ParseResult, urlparse

from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from django.shortcuts import render
from django.utils.html import urlize
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


def get_sentry_host():
    result: ParseResult = urlparse(settings.SENTRY_DSN)
    host = f"{result.scheme}://{result.hostname}"
    if result.port:
        host = f"{host}:{result.port}"

    return host


def get_sentry_dashboard():
    if getattr(settings, "SENTRY_PROJECT", None):
        return f"{get_sentry_host()}/{settings.SENTRY_PROJECT}"
    return 'N/A'


def get_event_url(event_id):
    try:
        return f"{get_sentry_host()}/{settings.SENTRY_PROJECT}/?query={event_id}"
    except Exception as e:
        logger.exception(e)


def make_sentry_link(event_id):
    if getattr(settings, "SENTRY_PROJECT", ""):
        try:
            return f'<a href="{get_event_url(event_id)}">{event_id}</a>'
        except Exception as e:
            logger.exception(e)
    return event_id


class SentryForm(forms.Form):
    ACTIONS = [
        ("capture_event", "capture_event()"),
        ("capture_exception", "capture_exception"),
        ("capture_message", "capture_message"),
        ("logging_integration", "logging_integration"),
        ("400", "Error 400"),
        ("403", "Error 403"),
        ("404", "Error 404"),
        ("500", "Error 500"),
    ]

    action = forms.ChoiceField(choices=ACTIONS, widget=forms.RadioSelect)


def panel_sentry(self, request, extra_context=None):
    import sentry_sdk
    context = self.each_context(request)
    context["title"] = "Sentry"
    context["info"] = {
        "SENTRY_DSN": settings.SENTRY_DSN,
        "SENTRY_SERVER_URL": mark_safe(urlize(get_sentry_host())),
        "SENTRY_DASHBOARD": mark_safe(urlize(get_sentry_dashboard())),
        "SENTRY_PROJECT": getattr(settings, "SENTRY_PROJECT", "N/A") or "N/A",
        "SENTRY_ENVIRONMENT": getattr(settings, "SENTRY_ENVIRONMENT", "N/A") or "N/A",
    }
    if request.method == "POST":
        form = SentryForm(request.POST)
        if form.is_valid():
            last_event_id = None
            opt = form.cleaned_data["action"]
            if opt == "capture_event":
                last_event_id = sentry_sdk.capture_event({"capture_event() Test": 1})
            elif opt == "capture_exception":
                last_event_id = sentry_sdk.capture_exception(Exception("capture_exception() Test"))
            elif opt == "capture_message":
                last_event_id = sentry_sdk.capture_message("capture_message() Test")
            elif opt == "logging_integration":
                try:
                    raise Exception("Logging Integration/last_event_id() Test")
                except Exception as e:
                    logger.exception(e)
                    last_event_id = sentry_sdk.last_event_id()
            elif opt in ["400", "403", "404", "500"]:
                from django.conf.urls import handler400, handler403, handler404, handler500
                mapping = {
                    "400": (ValidationError, handler400),
                    "403": (PermissionDenied, handler403),
                    "404": (Http404, handler404),
                    "500": (Exception, handler500),
                }
                error, handler = mapping[opt]
                try:
                    raise error(f"Error {opt} Test")
                except Exception as e:
                    logger.exception(e)
                    last_event_id = sentry_sdk.last_event_id()
                    handler(request, e)
            messages.add_message(request, messages.SUCCESS,
                                 mark_safe(f"Sentry ID: {make_sentry_link(last_event_id)}"))

    else:
        form = SentryForm()
    context["form"] = form
    return render(request, "smart_admin/panels/sentry.html", context)


panel_sentry.verbose_name = _("Sentry")
panel_sentry.url_name = "sentry"
