from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import (AllValuesComboFilter,
                                  PermissionPrefixFilter, TextFieldFilter, )
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import (GroupAdmin as _GroupAdmin,
                                       UserAdmin as _UserAdmin, )
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import render
from django.utils.translation import gettext as _

from smart_admin.decorators import smart_register

User = get_user_model()


@smart_register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    list_display = ('app_label', 'model')
    search_fields = ('model',)
    list_filter = (('app_label', AllValuesComboFilter),)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@smart_register(Permission)
class PermissionAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('name', 'content_type', 'codename')
    search_fields = ('name',)
    list_filter = (('content_type', AutoCompleteFilter),
                   PermissionPrefixFilter,)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
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


@smart_register(User)
class UserAdmin(ExtraUrlMixin, _UserAdmin):
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    @button()
    def permissions(self, request, pk):
        # User = get_user_model()
        context = self.get_common_context(request, pk,
                                          title=_("Permissions"),
                                          aeu_groups=['1'])
        context['permissions'] = sorted(context['original'].get_all_permissions())
        # group = context['original']
        # users = User.objects.filter(groups=group).distinct()
        # context['title'] = _('Users in group "%s"') % group.name
        # context['user_opts'] = User._meta
        # context['data'] = users

        return render(request, 'admin/auth/user/permissions.html', context)

@smart_register(Group)
class GroupAdmin(ExtraUrlMixin, _GroupAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    @button()
    def users(self, request, pk):
        User = get_user_model()
        context = self.get_common_context(request, pk, aeu_groups=['1'])
        group = context['original']
        users = User.objects.filter(groups=group).distinct()
        context['title'] = _('Users in group "%s"') % group.name
        context['user_opts'] = User._meta
        context['data'] = users

        return render(request, 'admin/auth/group/users.html', context)
