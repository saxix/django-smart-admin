from adminfilters.filters import ChoicesFieldComboFilter
from django.contrib.admin import ModelAdmin, FieldListFilter

from smart_admin.changelist import SmartChangeListMixin
from smart_admin.mixins import SmartMixin


class SmartModelAdmin(SmartMixin, SmartChangeListMixin, ModelAdmin):


    def get_list_filter(self, request):
        return super().get_list_filter(request)
