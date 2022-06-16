from admin_extra_buttons.api import ExtraButtonsMixin, button
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import AllValuesComboFilter, PermissionPrefixFilter
from adminfilters.mixin import AdminFiltersMixin
from django.apps import apps
from django.contrib import admin
from django.contrib.admin.utils import construct_change_message
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as _GroupAdmin, UserAdmin as _UserAdmin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.management import get_contenttypes_and_models
from django.contrib.contenttypes.management.commands.remove_stale_contenttypes import NoFastDeleteCollector
from django.contrib.contenttypes.models import ContentType
from django.db import DEFAULT_DB_ALIAS
from django.db.models import Q
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _

from ..views import SmartAutocompleteJsonView

User = get_user_model()


class SmartContentTypeJsonView(SmartAutocompleteJsonView):

    def get_label(self, obj):
        return f'{obj.name.title()} ({obj.app_label})'


# @smart_register(ContentType)
class ContentTypeAdmin(ExtraButtonsMixin, AdminFiltersMixin, admin.ModelAdmin):
    list_display = ('app_label', 'model')
    search_fields = ('model',)
    list_filter = (('app_label', AllValuesComboFilter),)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def autocomplete_view(self, request):
        return SmartContentTypeJsonView.as_view(model_admin=self)(request)

    @button(permission='contenttypes.delete_contenttype')
    def check_stale(self, request):  # noqa
        context = self.get_common_context(request, title='Stale')
        to_remove = {}
        if request.method == 'POST':
            cts = request.POST.getlist('ct')
            with atomic():
                ContentType.objects.filter(id__in=cts).delete()
            self.message_user(request, f'Removed {len(cts)} stale ContentTypes')
        else:
            def _collect_linked(ct):
                collector = NoFastDeleteCollector(using=DEFAULT_DB_ALIAS)
                collector.collect([ct])
                for obj_type, objs in collector.data.items():
                    if objs == {ct}:
                        continue
                    for o in objs:
                        try:
                            to_remove[ct].append(f"{o.__class__.__name__} {o.pk} - {str(o)}")
                        except AttributeError:
                            to_remove[ct].append(f"{o.__class__.__name__} {o.pk}")

            for app_config in apps.get_app_configs():
                content_types, app_models = get_contenttypes_and_models(app_config, DEFAULT_DB_ALIAS,
                                                                        ContentType)
                if not app_models:
                    continue
                for (model_name, ct) in content_types.items():
                    if model_name not in app_models:
                        to_remove[ct] = []
                        _collect_linked(ct)

            for ct in ContentType.objects.all():
                if ct.app_label not in apps.app_configs.keys():
                    if ct not in to_remove:
                        to_remove[ct] = []
                        _collect_linked(ct)

            context['to_remove'] = dict(sorted(to_remove.items(),
                                               key=lambda x: f"{x[0].app_label} {x[0].model}"))
            return TemplateResponse(request,
                                    'smart_admin/smart_auth/contenttype/stale.html',
                                    context)


class PermissionAdmin(ExtraButtonsMixin, AdminFiltersMixin, admin.ModelAdmin):
    list_display = ('name', 'content_type', 'codename')
    search_fields = ('name',)
    list_filter = (('content_type', AutoCompleteFilter),
                   PermissionPrefixFilter,)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @button(label='Users/Groups')
    def users(self, request, pk):
        User = get_user_model()
        context = self.get_common_context(request, pk, aeu_groups=['1'])
        perm = context['original']
        users = User.objects.filter(Q(user_permissions=perm) | Q(groups__permissions=perm)).distinct()
        groups = Group.objects.filter(permissions=perm).distinct()
        context['title'] = _('Users/Groups with "%s"') % perm.name

        context['user_opts'] = User._meta
        context['data'] = {'users': users,
                           'groups': groups}

        return render(request, 'admin/auth/permission/users.html', context)


# @smart_register(User)
class UserAdmin(ExtraButtonsMixin, AdminFiltersMixin, _UserAdmin):
    list_filter = ('is_staff', 'is_superuser', 'is_active',
                   ('groups', AutoCompleteFilter),
                   )

    @button()
    def permissions(self, request, pk):
        context = self.get_common_context(request, pk,
                                          title=_("Permissions"),
                                          aeu_groups=['1'])
        context['permissions'] = sorted(context['original'].get_all_permissions())
        return render(request, 'admin/auth/user/permissions.html', context)

    @button(urls=['redir_to_perm/(?P<perm>.*)/$'])
    def redir_to_perm(self, request, perm):
        app_label, codename = perm.split('.')
        perm = Permission.objects.get(codename=codename, )
        url = reverse("admin:auth_permission_change", args=[perm.pk])
        return HttpResponseRedirect(url)

    def _groups(self, request, object_id) -> set:
        return set(self.get_object(request, object_id).groups.values_list("name", flat=True))

    def _perms(self, request, object_id) -> set:
        return set(self.get_object(request, object_id).user_permissions.values_list("codename", flat=True))

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if object_id:
            self.existing_perms = self._perms(request, object_id)
            self.existing_groups = self._groups(request, object_id)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def construct_change_message(self, request, form, formsets, add=False):
        change_message = construct_change_message(form, formsets, add)
        if not add and 'user_permissions' in form.changed_data:
            new_perms = self._perms(request, form.instance.id)
            change_message[0]['changed']['permissions'] = {"added": sorted(new_perms.difference(self.existing_perms)),
                                                           "removed": sorted(self.existing_perms.difference(new_perms)),
                                                           }
        if not add and 'groups' in form.changed_data:
            new_groups = self._groups(request, form.instance.id)
            change_message[0]['changed']['groups'] = {"added": sorted(new_groups.difference(self.existing_groups)),
                                                      "removed": sorted(self.existing_groups.difference(new_groups)),
                                                      }
        return change_message


# @smart_register(Group)
class GroupAdmin(ExtraButtonsMixin, _GroupAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    @button()
    def members(self, request, pk):
        User = get_user_model()
        context = self.get_common_context(request, pk, aeu_groups=['1'])
        group = context['original']
        users = User.objects.filter(groups=group).distinct()
        context['title'] = _('Members')
        context['user_opts'] = User._meta
        context['data'] = users
        return render(request, 'admin/auth/group/members.html', context)

    def _perms(self, request, object_id) -> set:
        return set(self.get_object(request, object_id).permissions.values_list("codename", flat=True))

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if object_id:
            self.existing_perms = self._perms(request, object_id)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def construct_change_message(self, request, form, formsets, add=False):
        change_message = construct_change_message(form, formsets, add)
        if not add and 'permissions' in form.changed_data:
            new_perms = self._perms(request, form.instance.id)
            change_message[0]['changed']['permissions'] = {"added": sorted(new_perms.difference(self.existing_perms)),
                                                           "removed": sorted(self.existing_perms.difference(new_perms)),
                                                           }
        return change_message
