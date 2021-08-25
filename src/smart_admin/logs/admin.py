from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin, _confirm_action
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import RelatedFieldComboFilter
from django.contrib import admin
from django.contrib.admin import register
from django.contrib.admin.models import LogEntry
from django.utils.translation import gettext as _

from smart_admin.mixins import SmartMixin
from smart_admin.truncate import truncate_model_table


@register(LogEntry)
class LogEntryAdmin(SmartMixin, ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('action_time', 'user', 'action_flag', 'content_type', 'object_repr')
    readonly_fields = ('__all__',)
    search_fields = ('object_repr',)
    list_filter = (('user', AutoCompleteFilter),
                   ('content_type', RelatedFieldComboFilter),
                   'action_time',
                   'action_flag')
    date_hierarchy = 'action_time'

    @button(permission="truncate_logentry")
    def truncate(self, request):
        def _doit(request):
            truncate_model_table(LogEntry)
            self.message_user(request, _("All records have been removed"))

        return _confirm_action(self, request, _doit, "", "",
                               extra_context=self.get_common_context(request, title="Erase all data"),
                               template="smart_admin/truncate.html")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'content_type')
