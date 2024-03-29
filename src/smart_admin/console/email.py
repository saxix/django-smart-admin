import concurrent.futures
import logging
import threading

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from smart_admin.utils import masker

logger = logging.getLogger(__name__)


class ThreadWithReturnValue(threading.Thread):
    def __init__(self, *init_args, **init_kwargs):
        threading.Thread.__init__(self, *init_args, **init_kwargs)
        self._return = None

    def run(self):
        self._return = self._target(*self._args, **self._kwargs)

    def join(self, timeout=None):
        threading.Thread.join(self)
        return self._return


def panel_email(self, request, extra_context=None):
    context = self.each_context(request)
    context["title"] = "Test Email"
    context["smtp"] = {
        "EMAIL_BACKEND": settings.EMAIL_BACKEND,
        "EMAIL_HOST": settings.EMAIL_HOST,
        "EMAIL_PORT": settings.EMAIL_PORT,
        "EMAIL_HOST_PASSWORD": masker(settings.EMAIL_HOST_PASSWORD, request),
        "EMAIL_HOST_USER": settings.EMAIL_HOST_USER,
        "EMAIL_USE_SSL": settings.EMAIL_USE_SSL,
        "EMAIL_USE_TLS": settings.EMAIL_USE_TLS,
        "DEFAULT_FROM_EMAIL": settings.DEFAULT_FROM_EMAIL,
    }
    logs = []
    if request.method == "POST":
        try:
            from django.core.mail import get_connection
            conn = get_connection()
            context["connection"] = conn
            from django.core.mail import send_mail
            kwargs = {
                "subject": "Send email test: 'django.core.mail.send_mail'",
                "from_email": None,
                "message": "Test send email using raw 'django.core.mail.send_mail'",
                "recipient_list": [request.user.email],
            }
            logs.append([timezone.now(), "Thread started"])
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(send_mail, **kwargs)
                exc = future.exception()
                if exc:
                    messages.add_message(request, messages.ERROR, f"{exc.__class__.__name__}: {exc}")
                    logs.append([timezone.now(), f"Thread error {exc}"])
                else:
                    return_value = future.result()
                    logs.append([timezone.now(), f"Thread completed {return_value}"])
                    if return_value == 1:
                        messages.add_message(request, messages.SUCCESS, f"Email sent to {request.user.email}")
        except Exception as e:
            logger.exception(e)
            messages.add_message(request, messages.ERROR, f"{e.__class__.__name__}: {e}")
    context["logs"] = logs
    return render(request, "smart_admin/panels/email.html", context)


panel_email.verbose_name = _("Test Email")  # type: ignore[attr-defined]
panel_email.url_name = "email"  # type: ignore[attr-defined]
