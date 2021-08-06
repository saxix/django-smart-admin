import datetime
import sys

import factory
import factory.fuzzy
from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin, _confirm_action
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import MaxMinFilter, TextFieldFilter, PermissionPrefixFilter, AllValuesComboFilter
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import register
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import OperationalError
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from factory import SubFactory
from factory.django import DjangoModelFactory

import smart_admin.settings as smart_settings
from smart_admin.decorators import smart_register
from smart_admin.mixins import SmartMixin

from .models import DemoModel1, DemoModel2, DemoModel3, DemoModel4


class UserFactory(DjangoModelFactory):
    username = factory.Sequence(lambda i: f'username-{i}')
    email = factory.Faker('email')
    is_staff = False
    is_active = False
    is_superuser = False

    class Meta:
        model = User
        django_get_or_create = ('username',)


class DemoModel1Factory(DjangoModelFactory):
    name = factory.Faker('name')
    email = factory.Faker('email')
    char = factory.fuzzy.FuzzyText()
    integer = factory.fuzzy.FuzzyInteger(100)
    date = factory.fuzzy.FuzzyDate(datetime.date(2008, 1, 1))
    user = SubFactory(UserFactory)

    class Meta:
        model = DemoModel1


@register(DemoModel1)
class Admin1(SmartMixin, ExtraUrlMixin, admin.ModelAdmin):
    list_filter = (('user', AutoCompleteFilter),
                   'date',
                   ('integer', MaxMinFilter),
                   TextFieldFilter.factory('user__email')
                   )

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

    @button()
    def create_100_records(self, request):
        DemoModel1Factory.create_batch(100)

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
                mark_safe(
                    """
<h1 class="color-red"><b>This is a low level system feature</b></h1>                                      
<h1 class="color-red"><b>Continuing irreversibly delete all table content</b></h1>
                                       
                                       """
                ),
                "Successfully executed",
                title="Truncate table",
            )


@register(DemoModel2)
class Admin2(SmartMixin, admin.ModelAdmin):
    pass


@register(DemoModel3)
class Admin3(admin.ModelAdmin):
    pass


@register(DemoModel4)
class Admin4(admin.ModelAdmin):
    pass


from django.contrib.auth.admin import UserAdmin as _UserAdmin


@smart_register(User)
class UserAdmin(_UserAdmin):
    list_filter = (
        TextFieldFilter.factory('email', 'Email'),
        PermissionPrefixFilter,
        'is_staff', 'is_superuser', 'is_active', 'groups')


@smart_register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'content_type', 'codename')
    search_fields = ('name',)
    list_filter = (('content_type', AutoCompleteFilter),
                   PermissionPrefixFilter,)


@smart_register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    list_display = ('app_label', 'model')
    search_fields = ('model',)
    list_filter = (('app_label', AllValuesComboFilter),)
