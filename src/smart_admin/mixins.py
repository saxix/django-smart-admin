from itertools import chain

from admin_extra_buttons.api import ExtraButtonsMixin, button
from adminfilters.filters import AllValuesComboFilter, ChoicesFieldComboFilter, RelatedFieldComboFilter
from adminfilters.mixin import AdminFiltersMixin
from django.contrib import admin, messages
from django.contrib.admin import FieldListFilter
from django.contrib.admin.checks import BaseModelAdminChecks, must_be
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.admin.utils import flatten
from django.contrib.contenttypes.models import ContentType
from django.db import OperationalError, models, transaction, IntegrityError
from django.db.models import AutoField, ForeignKey, ManyToManyField, TextField
from django.db.models.fields.related import RelatedField
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from smart_admin.truncate import truncate_model_table
from smart_admin.utils import get_linked_objects

from .changelist import SmartChangeListMixin


class SmartFilterMixin:
    def __init__(self, model, admin_site):
        FieldListFilter.register(lambda f: bool(f.choices), ChoicesFieldComboFilter, True)
        FieldListFilter.register(lambda f: isinstance(f, models.BooleanField), AllValuesComboFilter, True)
        FieldListFilter.register(lambda f: f.remote_field, RelatedFieldComboFilter, True)

        super().__init__(model, admin_site)  # type: ignore[call-arg]


class SmartAutoFilterMixin(SmartFilterMixin):
    def __init__(self, model, admin_site):
        self.model = model
        self.list_filter = self._get_list_filter()
        super().__init__(model, admin_site)

    def _get_list_filter(self):
        if self.list_filter:
            return self.list_filter
        return [
            field.name
            for field in self.model._meta.fields
            if field.db_index
            and not isinstance(
                field,
                AutoField | RelatedField | TextField,
            )
        ]


class DisplayAllMixin:
    def get_list_display(self, request):  # pragma: no cover
        if self.list_display == ("__str__",):
            return [
                field.name
                for field in self.model._meta.fields
                if not isinstance(field, AutoField | ForeignKey | TextField | ManyToManyField)
            ]

        return self.list_display


class FieldsetMixin:
    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj)  # type: ignore[misc]

    def get_fieldsets(self, request, obj=None):
        all_fields = self.get_fields(request, obj)
        selected = []

        if self.fieldsets:
            fieldsets = list(self.fieldsets)
        else:
            fieldsets = [(None, {"fields": all_fields})]

        for e in fieldsets:
            selected.extend(flatten(e[1]["fields"]))
        __all = [e for e in all_fields if e not in selected]
        for e in fieldsets:
            if e[1]["fields"] == ("__others__",):
                e[1]["fields"] = __all
        return fieldsets


class SmartModelAdminChecks(BaseModelAdminChecks):
    def _check_readonly_fields(self, obj: admin.ModelAdmin):
        """Check that readonly_fields refers to proper attribute or field."""
        if obj.readonly_fields == ("__all__",):
            return []
        if obj.readonly_fields == ():
            return []
        if not isinstance(obj.readonly_fields, list | tuple):
            return must_be("a list or tuple", option="readonly_fields", obj=obj, id="admin.E034")
        return list(
            chain.from_iterable(
                self._check_readonly_fields_item(obj, field_name, "readonly_fields[%d]" % index)
                for index, field_name in enumerate(obj.readonly_fields)
            )
        )


class ReadOnlyMixin(admin.ModelAdmin):
    readonly_fields: tuple[str] = ("__all__",)
    checks_class = SmartModelAdminChecks

    def get_readonly_fields(self, request, obj=None):
        if self.readonly_fields and self.readonly_fields == ("__all__",):
            return list(
                set(
                    [field.name for field in self.opts.local_fields]
                    + [field.name for field in self.opts.local_many_to_many]
                )
            )
        return self.readonly_fields


class SmartMixin(
    ReadOnlyMixin, ExtraButtonsMixin, FieldsetMixin, DisplayAllMixin, SmartChangeListMixin, AdminFiltersMixin
):
    readonly_fields: tuple[str] = ()


class LinkedObjectsMixin(admin.ModelAdmin):
    linked_objects_template = None
    linked_objects_hide_empty = True
    linked_objects_max_records = 200
    linked_objects_exclude: list[str] = []
    linked_objects_filter: list[str] | None = None
    linked_objects_link_to_changelist = True

    def get_excluded_linked_objects(self, request) -> list:
        return self.linked_objects_exclude

    def get_selected_linked_objects(self, request) -> list:
        return self.linked_objects_filter

    def get_linked_objects(self, request, original):
        return get_linked_objects(
            original,
            self.get_excluded_linked_objects(request),
            self.get_selected_linked_objects(request),
            max_records=self.linked_objects_max_records,
            include_empty=not self.linked_objects_hide_empty,
        )

    @button()
    def linked_objects(self, request, pk) -> TemplateResponse:
        opts = self.model._meta
        app_label = opts.app_label
        context = self.get_common_context(request, pk, title="linked objects")
        linked, empty = self.get_linked_objects(request, context["original"])
        context["hide_empty"] = not self.linked_objects_hide_empty
        context["empty"] = sorted(empty, key=lambda x: x["related_name"].lower())
        context["linked"] = sorted(linked, key=lambda x: x["related_name"].lower())

        return TemplateResponse(
            request,
            self.linked_objects_template
            or [
                f"admin/{app_label}/{opts.model_name}/linked_objects.html",
                "admin/%s/linked_objects.html" % app_label,
                "smart_admin/linked_objects.html",
            ],
            context,
        )


def log_truncate(request, model):
    from django.contrib.admin.models import DELETION, LogEntry

    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(model).pk,
        object_id=None,
        object_repr=f"truncate table {model._meta.verbose_name}",
        action_flag=DELETION,
        change_message="truncate table",
    )


class TruncateAdminMixin:
    truncate_table_template = "smart_admin/truncate_table.html"

    def _truncate(self, request):
        opts = self.model._meta
        context = self.get_common_context(request, opts=opts)

        if request.method == "POST":
            with transaction.atomic():  # Outer atomic, start a new transaction
                transaction.on_commit(lambda: log_truncate(request, self.model))
                try:
                    truncate_model_table(self.model)
                    self.message_user(request, "Table truncated", messages.SUCCESS)
                except (OperationalError, IntegrityError):
                    self.message_user(request, "Truncate failed.", messages.WARNING)
                url = reverse(admin_urlname(opts, "changelist"))
                return HttpResponseRedirect(url)
        else:
            return TemplateResponse(request, self.truncate_table_template, context)
