from django.contrib import admin
from django.contrib.admin import register

from smart_admin.mixins import SmartMixin
from .models import DemoModel1, DemoModel2, DemoModel3, DemoModel4


@register(DemoModel1)
class Admin1(SmartMixin, admin.ModelAdmin):
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


@register(DemoModel2)
class Admin2(SmartMixin, admin.ModelAdmin):
    pass


@register(DemoModel3)
class Admin3(admin.ModelAdmin):
    pass


@register(DemoModel4)
class Admin4(admin.ModelAdmin):
    pass
