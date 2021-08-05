import time
from collections import OrderedDict

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from functools import update_wrapper

from django.conf import settings
from django.contrib.admin import AdminSite
from django.core.cache import caches
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache

from . import get_full_version
from . import settings as smart_settings
from .settings import process_lazy
from .templatetags.smart import as_bool
from .utils import SmartList

cache = caches['default']


def _parse_section():
    base = smart_settings.SECTIONS
    ret = {'_hidden_': []}
    for name, entries in base.items():
        ret[name] = SmartList(entries)
    if 'Other' not in ret:
        ret['Other'] = []
    return ret


class SmartAdminSite(AdminSite):
    sysinfo_url = False
    index_template = 'admin/index.html'

    def get_bookmarks(self, request):
        if smart_settings.BOOKMARKS_PERMISSION is None or request.user.has_permission(
                smart_settings.BOOKMARKS_PERMISSION):
            bookmarks = []
            values = process_lazy('BOOKMARKS')

            for entry in values:
                if isinstance(entry, str):
                    label, url, cls = entry, entry, 'viewlink'
                elif len(entry) == 2:
                    label, url, cls = entry[0], entry[1], 'viewlink'
                elif len(entry) == 3:
                    label, url, cls = entry
                else:
                    raise ValueError(f"Invalid entry '{entry}' for BOOKMARKS")
                bookmarks.append([label, url, cls])
            return bookmarks
        return []

    def each_context(self, request):
        context = super().each_context(request)
        context['sysinfo'] = self.sysinfo_url
        context['smart_settings'] = smart_settings
        context['enable_switch'] = smart_settings.ENABLE_SWITCH
        context['bookmarks'] = self.get_bookmarks(request)
        context['smart'] = self.is_smart_enabled(request)
        context['smart_sections'], context['model_to_section'] = self._get_menu(request)
        context['adminsite'] = self
        if smart_settings.PROFILE_LINK and request.user.is_authenticated:
            context['profile_link'] = reverse(admin_urlname(request.user._meta, 'change'),
                                              args=[request.user.pk])

        return context

    def is_smart_enabled(self, request):
        return as_bool(request.COOKIES.get('smart', "0"))

    @never_cache
    def index(self, request, extra_context=None):
        if self.is_smart_enabled(request):
            return self.smart_index(request)
        else:
            return super().index(request)

    def admin_sysinfo(self, request):
        from django_sysinfo.api import get_sysinfo
        infos = get_sysinfo(request)
        infos.setdefault('extra', {})
        infos.setdefault('checks', {})
        from django.contrib.admin import site
        context = self.each_context(request)
        context.update({'title': 'sysinfo',
                        'infos': infos,
                        # 'site_title': site.site_title,
                        # 'site_header': site.site_header,
                        'enable_switch': True,
                        'has_permission': True,
                        # 'user': request.user,
                        })
        return render(request, 'admin/sysinfo/sysinfo.html', context)

    def app_index(self, request, app_label, extra_context=None):
        groups, __ = self._get_menu(request)
        if app_label not in groups:
            request.COOKIES['smart'] = "0"
        if self.is_smart_enabled(request):
            self.app_index_template = 'admin/group_index.html'
        response = super().app_index(request, app_label, extra_context)
        response.set_cookie("smart", )
        return response

    def smart_toggle(self, request, on_off):
        path = request.GET.get('from', request.path)
        response = HttpResponseRedirect(path)
        response.set_cookie('smart', int(as_bool(on_off)))
        return response

    def get_urls(self):
        from django.urls import path

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)

            wrapper.admin_site = self
            return update_wrapper(wrapper, view)

        urlpatterns = [path('~groups/<str:group>/', wrap(self.smart_section), name='group_list'),
                       path('smart/<str:on_off>/', wrap(self.smart_toggle), name='smart_toggle'),
                       # path('sysinfo/', wrap(admin_sysinfo), name='222'),
                       ]

        try:
            if 'django_sysinfo' in settings.INSTALLED_APPS:
                from django.urls import reverse_lazy
                urlpatterns += [path('~sysinfo/', wrap(self.admin_sysinfo), name='smart-sysinfo-admin'), ]
                self.sysinfo_url = reverse_lazy('admin:smart-sysinfo-admin')
        except ImportError:
            pass
        urlpatterns += super().get_urls()

        return urlpatterns

    def _get_menu(self, request):
        if settings.DEBUG:  # pragma: no cover
            ver = time.time
        else:
            ver = get_full_version
        sections = _parse_section()
        key1 = f'{hash(repr(sections))}:groups:{ver()}'
        key2 = f'{hash(repr(sections))}:models:{ver()}'

        groups = cache.get(key1)
        model_to_section = cache.get(key2)
        if not (groups and model_to_section):
            model_to_section = {}
            groups = OrderedDict([(k, []) for k in sections.keys()])
            app_list = self.get_app_list(request)

            def get_section(model, app):
                fqn = '%s.%s' % (app['app_label'], model['object_name'])
                target = 'Other'
                if fqn in sections['_hidden_'] or app['app_label'] in sections['_hidden_']:
                    return '_hidden_'

                for sec, models in sections.items():
                    if fqn in models:
                        return sec
                    elif app['app_label'] in models:
                        return sec
                return target

            for app in app_list:
                for model in app['models']:
                    sec = get_section(model, app)
                    model_to_section[f"{app['app_label']}.{model['object_name']}"] = sec
                    groups[sec].append(
                        {'app_label': str(app['app_label']),
                         'app_name': str(app['name']),
                         'app_url': app['app_url'],
                         'label': '%s - %s' % (app['name'], model['name']),
                         'model_name': str(model['name']),
                         'admin_url': model['admin_url'],
                         'perms': model['perms']})
            for __, models in groups.items():
                models.sort(key=lambda x: x['label'])
            cache.set(key1, groups, 60 * 60)
            cache.set(key2, model_to_section, 60 * 60)
        return groups, model_to_section

    @never_cache
    def smart_section(self, request, extra_context=None, group=None):
        # app_list = self.get_app_list(request)
        groups, __ = self._get_menu(request)
        section = groups[group]
        context = {
            **self.each_context(request),
            # 'smart': 1,
            # 'title': self.index_title,
            'app_list': [group],
            'groups': {group: section},
            **(extra_context or {}),
        }
        return TemplateResponse(request, 'admin/group_index.html', context)

    @never_cache
    def smart_index(self, request, extra_context=None):
        groups, __ = self._get_menu(request)
        context = {
            **self.each_context(request),
            'groups': dict(groups),
            **(extra_context or {}),
        }
        request.current_app = self.name
        return TemplateResponse(request, 'admin/smart_index.html', context)
