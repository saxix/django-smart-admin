from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin, _confirm_action
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import (TextFieldFilter, NumberFilter, )
from django.contrib import admin
from django.contrib.admin import register, TabularInline
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.contenttypes.models import ContentType
from django.db import OperationalError
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from smart_admin.smart_auth.admin import UserAdmin as SmartUserAdmin

import smart_admin.settings as smart_settings
from smart_admin.mixins import SmartMixin, LinkedObjectsMixin

from . import models
from .factories import get_factory_for_model


class FactoryMixin:
    @button()
    def create_sample_records(self, request):
        factory = get_factory_for_model(self.model)
        factory.create_batch(10)


@register(models.Customer)
class CustomerAdmin1(FactoryMixin, LinkedObjectsMixin, SmartMixin, ExtraUrlMixin, admin.ModelAdmin):
    list_display = ("name", "useremail", "email")

    list_filter = (('user', AutoCompleteFilter),
                   # ('integer', MaxMinFilter),
                   # ('logic', BooleanRadioFilter),
                   TextFieldFilter.factory('user__email'),
                   TextFieldFilter.factory('email')
                   )
    readonly_fields = ('user',)
    fieldsets = [
        (None, {"fields": (("name", "email"),)}),
        (
            "Set 1",
            {
                "classes": ("collapse",),
                "fields": (
                    "user",
                    "active",
                    "registration_date",
                ),
            },
        ),
        ("Others", {"classes": ("collapse",), "fields": ("__others__",)}),
    ]

    def useremail(self, obj):
        if obj.user:
            return obj.user.email

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

    @button(label="Truncate", css_class="btn-danger", permission=smart_settings.ISROOT)
    def truncate(self, request):
        # if not request.headers.get("x-root-access") == "XMLHttpRequest":
        #     self.message_user(request, "You are not allowed to perform this action", messages.ERROR)
        #     return
        if request.method == "POST":
            with atomic():
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(self.model).pk,
                    object_id=None,
                    object_repr=f"truncate table {self.model._meta.verbose_name}",
                    action_flag=DELETION,
                    change_message="truncate table",
                )
                from django.db import connections

                try:
                    conn = connections[self.model.objects.db]
                    cursor = conn.cursor()
                    cursor.execute('TRUNCATE TABLE "{0}" RESTART IDENTITY CASCADE '.format(self.model._meta.db_table))
                except OperationalError:
                    self.get_queryset(request).delete()
        else:
            return _confirm_action(
                self,
                request,
                self.truncate,
                mark_safe("""
<h1 class="color-red"><b>This is a low level system feature</b></h1>
<h1 class="color-red"><b>Continuing irreversibly delete all table content</b></h1>

                                       """),
                "Successfully executed",
                title="Truncate table",
            )


@register(models.Product)
class ProductAdmin(FactoryMixin, SmartMixin, ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('name', 'price', 'family')
    list_filter = ('family',)
    search_fields = ('name', )


@register(models.ProductFamily)
class ProductFamilyAdmin(FactoryMixin, SmartMixin, ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('name',)


class InvoiceItemInline(TabularInline):
    model = models.InvoiceItem
    extra = 0


@register(models.Invoice)
class InvoiceAdmin(FactoryMixin, SmartMixin, ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('number', 'date')
    list_filter = (('number', NumberFilter),
                   ('items__product', AutoCompleteFilter),
                   )
    search_fields = ('number',)
    inlines = [InvoiceItemInline]


@register(models.InvoiceItem)
class InvoiceItemAdmin(FactoryMixin, SmartMixin, ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('product', 'qty')
    list_filter = (('invoice', AutoCompleteFilter),)
    search_fields = ('qty',)


class UserAdmin(LinkedObjectsMixin, FactoryMixin, SmartUserAdmin):
    pass
