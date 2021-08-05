from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin, _confirm_action
from django.contrib import admin
from django.contrib.admin import register
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.http import HttpResponseRedirect
from django.urls import reverse

from smart_admin.mixins import SmartMixin
from .models import DemoModel1, DemoModel2, DemoModel3, DemoModel4


@register(DemoModel1)
class Admin1(SmartMixin, ExtraUrlMixin, admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": (("name", "char"),)}),
        (
            "Set 1",
            {
                "classes": ("collapse",),
                "fields": (
                    "integer",
                    "logic",
                    "decimal",
                    "date",
                ),
            },
        ),
        ("Others", {"classes": ("collapse",), "fields": ("__all__",)}),
    ]

    @button(label='Refresh', permission='demo.add_demomodel1')
    def refresh(self, request):
        opts = self.model._meta
        self.message_user(request, 'refresh called')
        return HttpResponseRedirect(reverse(admin_urlname(opts, 'changelist')))

    @button()
    def confirm(self, request):
        def _action(request):
            pass

        return _confirm_action(self, request, _action, "Confirm action",
                               "Successfully executed", )


@register(DemoModel2)
class Admin2(SmartMixin, admin.ModelAdmin):
    pass


@register(DemoModel3)
class Admin3(admin.ModelAdmin):
    pass


@register(DemoModel4)
class Admin4(admin.ModelAdmin):
    pass
