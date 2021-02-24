from itertools import chain

from adminfilters.filters import ChoicesFieldComboFilter, AllValuesComboFilter, RelatedFieldComboFilter
from django.contrib.admin import FieldListFilter
from django.contrib.admin.checks import BaseModelAdminChecks, must_be
from django.contrib.admin.utils import flatten
from django.db import models
from django.db.models import AutoField, TextField, ForeignKey, ManyToManyField
from django.db.models.fields.related import RelatedField


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
            if e[1]['fields'] == ('__all__',):
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


class SmartMixin(ReadOnlyMixin, FieldsetMixin, DisplayAllMixin):
    readonly_fields = ()
