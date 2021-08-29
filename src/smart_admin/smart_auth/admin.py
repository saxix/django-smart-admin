from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import AllValuesComboFilter, PermissionPrefixFilter
from django.contrib import admin
from django.contrib.admin.utils import construct_change_message
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import (GroupAdmin as _GroupAdmin,
                                       UserAdmin as _UserAdmin,)
from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _

User = get_user_model()


# @smart_register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    list_display = ('app_label', 'model')
    search_fields = ('model',)
    list_filter = (('app_label', AllValuesComboFilter),)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# @smart_register(Permission)
class PermissionAdmin(ExtraUrlMixin, admin.ModelAdmin):
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
class UserAdmin(ExtraUrlMixin, _UserAdmin):
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

    @button(urls=['redir_to_perm/(?P<perm>.*)/'])
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
class GroupAdmin(ExtraUrlMixin, _GroupAdmin):
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
