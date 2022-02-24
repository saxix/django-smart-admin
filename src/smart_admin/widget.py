from django import forms
from django.contrib.contenttypes.models import ContentType


class ContentTypeChoiceField(forms.ModelChoiceField):
    def __init__(self, *, empty_label="---------", required=True, widget=None, label=None,
                 initial=None, help_text="", to_field_name=None, limit_choices_to=None, **kwargs):
        queryset = ContentType.objects.order_by("model", "app_label")
        super().__init__(queryset, empty_label=empty_label, required=required, widget=widget,
                         label=label, initial=initial, help_text=help_text,
                         to_field_name=to_field_name, limit_choices_to=limit_choices_to, **kwargs)

    def label_from_instance(self, obj):
        return f"{obj.name.title()} ({obj.app_label})"
