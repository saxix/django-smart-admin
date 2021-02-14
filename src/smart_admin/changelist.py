from django.contrib.admin.views.main import ChangeList


class SmartChangeList(ChangeList):
    pass


class SmartChangeListMixin:
    readonly_fields = []

    def get_changelist(self, request, **kwargs):
        """
        Return the ChangeList class for use on the changelist page.
        """
        return SmartChangeList
