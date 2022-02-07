from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin, _confirm_action
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.depot.selector import FilterDepotManager
from adminfilters.filters import NumberFilter, ValueFilter, MaxMinFilter, BooleanRadioFilter, \
    MultiValueFilter
from django.contrib import admin
from django.contrib.admin import TabularInline, register, ModelAdmin
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.http import HttpResponseRedirect
from django.urls import reverse

from adminfilters.json import JsonFieldFilter
from adminfilters.querystring import QueryStringFilter
from smart_admin.mixins import LinkedObjectsMixin, SmartMixin, TruncateAdminMixin
from smart_admin.smart_auth.admin import UserAdmin as SmartUserAdmin

from . import models
from .factories import get_factory_for_model


class FactoryMixin(ModelAdmin):
    @button(html_attrs={"style": "background-color:#DC6C6C"})
    def create_sample_records(self, request):
        factory = get_factory_for_model(self.model)
        factory.create_batch(10)
        self.message_user(request, f"#10 records created")


@register(models.Customer)
class CustomerAdmin(FactoryMixin, LinkedObjectsMixin, SmartMixin, ExtraUrlMixin, admin.ModelAdmin):
    list_display = ("name", "useremail", "email", "flags")
    search_fields = ("name",)
    list_filter = (
        FilterDepotManager,
        QueryStringFilter,
        ('user', AutoCompleteFilter),
        ('flags', JsonFieldFilter),
        ('user__email', MultiValueFilter),
        # TextFieldFilter.factory('user__email'),
        ('email', ValueFilter)
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

    @button(html_attrs={"style": "background-color:#CAA61B;font-weight:bold"})
    def confirm(self, request):
        def _action(request):
            pass

        return _confirm_action(self, request, _action, "Confirm action",
                               "Successfully executed", )


@register(models.Product)
class ProductAdmin(FactoryMixin, SmartMixin, ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('name', 'price', 'family')
    list_filter = ('family',)
    search_fields = ('name',)


@register(models.ProductFamily)
class ProductFamilyAdmin(FactoryMixin, SmartMixin, ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('name',)


class InvoiceItemInline(TabularInline):
    model = models.InvoiceItem
    extra = 0


@register(models.Invoice)
class InvoiceAdmin(FactoryMixin, SmartMixin, ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('customer', 'number', 'date')
    list_filter = (('number', NumberFilter),
                   ('customer', AutoCompleteFilter),
                   ('items__product', AutoCompleteFilter),
                   )
    search_fields = ('number',)
    inlines = [InvoiceItemInline]


@register(models.InvoiceItem)
class InvoiceItemAdmin(FactoryMixin, SmartMixin, ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('product', 'qty')
    list_filter = (('invoice', AutoCompleteFilter),)
    search_fields = ('qty',)
    autocomplete_fields = ('product', 'invoice')


class UserAdmin(LinkedObjectsMixin, FactoryMixin, SmartUserAdmin):
    pass
