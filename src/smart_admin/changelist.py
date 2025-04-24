import logging

from django.contrib.admin.views.main import ChangeList

logger = logging.getLogger(__name__)


class SmartChangeList(ChangeList):
    pass


class SmartChangeListMixin:
    def get_changelist(self, request, **kwargs):
        """Return the ChangeList class for use on the changelist page."""
        return SmartChangeList
