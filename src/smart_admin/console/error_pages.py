import logging
from functools import partial

from django import forms
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class ErrorPageForm(forms.Form):
    ACTIONS = [
        ("400", "Error 400"),
        ("403", "Error 403"),
        ("404", "Error 404"),
        ("500", "Error 500"),
    ]

    action = forms.ChoiceField(choices=ACTIONS, widget=forms.RadioSelect)


def panel_error_page(self, request, extra_context=None):
    context = self.each_context(request)
    context["title"] = _("Error Pages")
    if request.method == "POST":
        form = ErrorPageForm(request.POST)
        if form.is_valid():
            opt = form.cleaned_data["action"]
            if opt in ["400", "403", "404", "500"]:
                from django.conf.urls import handler400, handler403, handler404, handler500
                mapping = {
                    "400": (ValidationError, partial(handler400, exception=ValidationError("Test Error"))),
                    "403": (ValidationError, partial(handler403, exception=PermissionDenied())),
                    "404": (ValidationError, partial(handler404, exception=Http404())),
                    "500": (ValidationError, partial(handler500)),
                }
                error, handler = mapping[opt]
                return handler(request)
    else:
        form = ErrorPageForm()
    context["form"] = form
    return render(request, "smart_admin/panels/sentry.html", context)


panel_error_page.verbose_name = _("Error Pages")
panel_error_page.url_name = "errors"
