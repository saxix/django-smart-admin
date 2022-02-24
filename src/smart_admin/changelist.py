import logging

from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.views.main import ChangeList

logger = logging.getLogger(__name__)


class SmartChangeList(ChangeList):
    def get_filters(self, request):
        try:
            return super().get_filters(request)
        except IncorrectLookupParameters as e:
            logger.exception(e)
            raise

    def get_results(self, request):
        try:
            return super().get_results(request)
        except IncorrectLookupParameters as e:
            logger.exception(e)
            raise

    def get_queryset(self, request):
        try:
            return super().get_queryset(request)
        except IncorrectLookupParameters as e:
            logger.exception(e)
            raise


class SmartChangeListMixin:
    readonly_fields = []

    def get_changelist(self, request, **kwargs):
        """
        Return the ChangeList class for use on the changelist page.
        """
        return SmartChangeList
