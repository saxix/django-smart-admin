import datetime
from admin_extra_buttons.api import ExtraButtonsMixin, button, confirm_action

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import RelatedFieldComboFilter
from django.contrib import admin
from django.contrib.admin import register
from django.contrib.admin.models import LogEntry
from django.utils.translation import gettext as _

from smart_admin.mixins import SmartMixin, TruncateAdminMixin


@register(LogEntry)
class LogEntryAdmin(SmartMixin, TruncateAdminMixin, ExtraButtonsMixin, admin.ModelAdmin):
    list_display = ('action_time', 'user', 'action_flag', 'content_type', 'object_repr')
    readonly_fields = ('__all__',)
    search_fields = ('object_repr',)
    list_filter = (('user', AutoCompleteFilter),
                   ('content_type', AutoCompleteFilter),
                   'action_time',
                   'action_flag')
    date_hierarchy = 'action_time'

    # @button(permission="admin.archive_logentry")
    @button()
    def archive(self, request):
        offset = datetime.date.today() - datetime.timedelta(days=365)
        offset_label = offset.strftime("%a, %b %d %Y")

        def _doit(request):
            LogEntry.objects.filter(action_time__lt=offset).delete()
            self.message_user(request, _("Records before %s have been removed") % offset_label)

        ctx = self.get_common_context(request,
                                      original=None,
                                      offset=offset_label,
                                      title="Removes old data")

        return confirm_action(self, request, _doit, "", "",
                              extra_context=ctx,
                              template="admin/logentry/archive.html")

    @button(label="Truncate", html_attrs={"class": "btn-danger"})
    def truncate(self, request):
        return super()._truncate(request)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'content_type')
