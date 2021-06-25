from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import RelatedFieldComboFilter
from django.contrib.admin import register
from django.contrib.admin.models import LogEntry
from django.contrib import admin

from smart_admin.mixins import SmartMixin



@register(LogEntry)
class LogEntryAdmin(SmartMixin, admin.ModelAdmin):
    readonly_fields = ('__all__',)
    list_filter = (('user', AutoCompleteFilter),
                   ('content_type', RelatedFieldComboFilter),
                   'action_flag')
    date_hierarchy = 'action_time'
