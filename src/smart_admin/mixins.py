from django.contrib import admin
from django.contrib.admin.utils import flatten
from django.db import models


class DisplayAllMixin:
    def get_list_display(self, request):  # pragma: no cover
        if self.list_display == ('__str__',):
            return [field.name for field in self.model._meta.fields
                    if not isinstance(field, models.ForeignKey)]

        return self.list_display


class FieldsetMixin(admin.ModelAdmin):

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


class ReadOnlyMixin:
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        if self.readonly_fields and self.readonly_fields == ('__all__',):
            return list(set(
                [field.name for field in self.opts.local_fields] +
                [field.name for field in self.opts.local_many_to_many]
            ))
        return self.readonly_fields


class SmartMixin(ReadOnlyMixin, FieldsetMixin, DisplayAllMixin):
    pass
