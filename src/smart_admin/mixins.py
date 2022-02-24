from itertools import chain

from admin_extra_buttons.api import ExtraButtonsMixin, button, confirm_action
from adminfilters.filters import AllValuesComboFilter, ChoicesFieldComboFilter, RelatedFieldComboFilter
from adminfilters.mixin import AdminFiltersMixin
from django.contrib.admin import FieldListFilter
from django.contrib.admin.checks import BaseModelAdminChecks, must_be
from django.contrib.admin.utils import flatten
from django.contrib.contenttypes.models import ContentType
from django.db import OperationalError, models
from django.db.models import AutoField, ForeignKey, ManyToManyField, TextField
from django.db.models.fields.related import RelatedField
from django.db.transaction import atomic
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe

from smart_admin.truncate import truncate_model_table
from smart_admin.utils import get_related

from .changelist import SmartChangeListMixin


class SmartFilterMixin:
    def __init__(self, model, admin_site):
        FieldListFilter.register(lambda f: bool(f.choices), ChoicesFieldComboFilter, True)
        FieldListFilter.register(lambda f: isinstance(f, models.BooleanField), AllValuesComboFilter, True)
        FieldListFilter.register(lambda f: f.remote_field, RelatedFieldComboFilter, True)

        super().__init__(model, admin_site)


class SmartAutoFilterMixin(SmartFilterMixin):
    def __init__(self, model, admin_site):
        self.model = model
        self.list_filter = self._get_list_filter()
        super().__init__(model, admin_site)

    def _get_list_filter(self):
        if self.list_filter:
            return self.list_filter
        return [field.name for field in self.model._meta.fields
                if field.db_index and not isinstance(field, (AutoField,
                                                             RelatedField,
                                                             # ManyToManyField,
                                                             # ForeignKey,
                                                             TextField))
                ]


class DisplayAllMixin:
    def get_list_display(self, request):  # pragma: no cover
        if self.list_display == ('__str__',):
            return [field.name for field in self.model._meta.fields
                    if not isinstance(field, (AutoField,
                                              ForeignKey,
                                              TextField, ManyToManyField))]

        return self.list_display


class FieldsetMixin:

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj)

    def get_fieldsets(self, request, obj=None):
        all_fields = self.get_fields(request, obj)
        selected = []

        if self.fieldsets:
            fieldsets = list(self.fieldsets)
        else:
            fieldsets = [(None, {'fields': all_fields})]

        for e in fieldsets:
            selected.extend(flatten(e[1]['fields']))
        __all = [e for e in all_fields if e not in selected]
        for e in fieldsets:
            if e[1]['fields'] == ('__others__',):
                e[1]['fields'] = __all
        return fieldsets


class SmartModelAdminChecks(BaseModelAdminChecks):
    def _check_readonly_fields(self, obj):
        """ Check that readonly_fields refers to proper attribute or field. """
        if obj.readonly_fields == ('__all__',):
            return []
        if obj.readonly_fields == ():
            return []
        elif not isinstance(obj.readonly_fields, (list, tuple)):
            return must_be('a list or tuple', option='readonly_fields', obj=obj, id='admin.E034')
        else:
            return list(chain.from_iterable(
                self._check_readonly_fields_item(obj, field_name, "readonly_fields[%d]" % index)
                for index, field_name in enumerate(obj.readonly_fields)
            ))


class ReadOnlyMixin:
    readonly_fields = ('__all__',)
    checks_class = SmartModelAdminChecks

    def get_readonly_fields(self, request, obj=None):
        if self.readonly_fields and self.readonly_fields == ('__all__',):
            return list(set(
                [field.name for field in self.opts.local_fields] +
                [field.name for field in self.opts.local_many_to_many]
            ))
        return self.readonly_fields


class SmartMixin(ReadOnlyMixin, ExtraButtonsMixin, FieldsetMixin, DisplayAllMixin, SmartChangeListMixin,
                 AdminFiltersMixin):
    readonly_fields = ()


class LinkedObjectsMixin:
    linked_objects_template = None

    def get_ignored_linked_objects(self):
        return []

    @button()
    def linked_objects(self, request, pk):
        ignored = self.get_ignored_linked_objects()
        opts = self.model._meta
        app_label = opts.app_label
        context = self.get_common_context(request, pk, title="linked objects")
        reverse = []
        for f in self.model._meta.get_fields():
            if f.auto_created and not f.concrete and f.name not in ignored:
                reverse.append(f)
        # context["reverse"] = [get_related(user, f ) for f in reverse]
        context["reverse"] = sorted([get_related(context['original'], f) for f in reverse],
                                    key=lambda x: x['related_name'].lower())

        return TemplateResponse(request, self.linked_objects_template or [
            "admin/%s/%s/linked_objects.html" % (app_label, opts.model_name),
            "admin/%s/linked_objects.html" % app_label,
            "smart_admin/linked_objects.html"
        ], context)


class TruncateAdminMixin:
    def _truncate(self, request):
        if request.method == "POST":
            from django.contrib.admin.models import DELETION, LogEntry
            with atomic():
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(self.model).pk,
                    object_id=None,
                    object_repr=f"truncate table {self.model._meta.verbose_name}",
                    action_flag=DELETION,
                    change_message="truncate table",
                )

                try:
                    truncate_model_table(self.model)
                except OperationalError:
                    self.get_queryset(request).delete()
        else:
            return confirm_action(
                self,
                request,
                self.truncate,
                mark_safe("""
<h1 class="color-red"><b>This is a low level system feature</b></h1>
<h1 class="color-red"><b>Continuing irreversibly delete all table content</b></h1>

                                       """),
                "Successfully executed",
                title="Truncate table",
                extra_context={"original": None, "add": False},
            )
