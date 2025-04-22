import logging

from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.views.main import ChangeList

from smart_admin.compat import IS_DJANGO4

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

    def get_queryset(self, request, exclude_parameters=None):
        try:
            if IS_DJANGO4:
                return super().get_queryset(request)
            return super().get_queryset(request, exclude_parameters)
        except IncorrectLookupParameters as e:
            logger.exception(e)
            raise


class SmartChangeListMixin:
    def get_changelist(self, request, **kwargs):
        """Return the ChangeList class for use on the changelist page."""
        return SmartChangeList
