from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.http import Http404, JsonResponse


class SmartAutocompleteJsonView(AutocompleteJsonView):
    def get_label(self, obj):
        return str(obj)

    def get(self, request, *args, **kwargs):
        if not self.model_admin.get_search_fields(request):
            raise Http404(
                '%s must have search_fields for the autocomplete_view.' %
                type(self.model_admin).__name__
            )
        if not self.has_perm(request):
            return JsonResponse({'error': '403 Forbidden'}, status=403)

        self.term = request.GET.get('term', '')
        self.paginator_class = self.model_admin.paginator
        self.object_list = self.get_queryset()
        context = self.get_context_data()

        return JsonResponse({
            'results': [
                {'id': str(obj.pk),
                 # 'text': f'{obj.name.title()} ({obj.app_label})'}
                 'text': self.get_label(obj)}
                for obj in context['object_list']
            ],
            'pagination': {'more': context['page_obj'].has_next()},
        })
