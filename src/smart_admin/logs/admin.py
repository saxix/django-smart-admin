from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import RelatedFieldComboFilter
from django.contrib.admin import register
from django.contrib.admin.models import LogEntry
from django.contrib import admin

from smart_admin.mixins import SmartMixin



@register(LogEntry)
class LogEntryAdmin(SmartMixin, admin.ModelAdmin):
    list_display = ('action_time', 'user', 'action_flag', 'content_type', 'object_repr')
    readonly_fields = ('__all__',)
    list_filter = (('user', AutoCompleteFilter),
                   ('content_type', RelatedFieldComboFilter),
                   'action_flag')
    date_hierarchy = 'action_time'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'content_type')
