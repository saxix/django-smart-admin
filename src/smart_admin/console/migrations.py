import io

from django.core.management import call_command
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


def panel_migrations(self, request):
    out = io.StringIO()
    call_command("showmigrations", stdout=out, no_color=True, format="list")
    context = self.each_context(request)
    context["list"] = out.getvalue()
    out = io.StringIO()
    call_command("showmigrations", stdout=out, no_color=True, format="plan")
    context["plan"] = out.getvalue()

    return render(request, "smart_admin/panels/migrations.html", context)


panel_migrations.verbose_name = _("Migrations")
panel_migrations.url_name = "migrations"
