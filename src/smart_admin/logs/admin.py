import datetime
import pytz
from django.conf import settings
from django.http import HttpRequest

from admin_extra_buttons.api import button, confirm_action, link
from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin
from django.contrib.admin import register
from django.contrib.admin.models import LogEntry
from django.utils.translation import gettext as _

from smart_admin.mixins import SmartMixin, TruncateAdminMixin
from smart_admin.settings import check_logentry_archive_perm


@register(LogEntry)
class LogEntryAdmin(SmartMixin, TruncateAdminMixin, admin.ModelAdmin):
    list_display = ("action_time", "user", "action_flag", "content_type", "object_repr")
    readonly_fields = ("__all__",)
    search_fields = ("object_repr",)
    list_filter = (("user", AutoCompleteFilter), ("content_type", AutoCompleteFilter), "action_time", "action_flag")
    date_hierarchy = "action_time"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @link(change_list=False)
    def edit_original(self, button):
        button.href = button.original.get_admin_url()
        button.title = button.original.object_repr

    @button(permission=check_logentry_archive_perm, html_attrs={"class": "aeb-danger"})
    def archive(self, request: HttpRequest):
        tz = pytz.timezone(settings.TIME_ZONE)
        today = datetime.datetime.today()
        offset = datetime.datetime.combine(
            today - datetime.timedelta(days=365), datetime.datetime.max.time()
        ).astimezone(tz)

        offset_label = offset.strftime("%a, %b %d %Y")
        count = LogEntry.objects.filter(action_time__lt=offset).count()

        def _doit(req: HttpRequest):
            LogEntry.objects.filter(action_time__lt=offset).delete()
            self.message_user(req, _("Records before %s have been removed") % offset_label)

        ctx = {"original": None, "offset": offset_label}

        return confirm_action(
            self,
            request,
            _doit,
            message="",
            description=_("{count} log entries will be deleted").format(count=count),
            success_message="",
            extra_context=ctx,
            template="admin/logentry/archive.html",
        )

    @button(label="Truncate", html_attrs={"class": "btn-danger"})
    def truncate(self, request):
        return super()._truncate(request)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "content_type")
