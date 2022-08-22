import time
from collections import OrderedDict
from functools import partial, update_wrapper

from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.cache import caches
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from . import get_full_version, settings as smart_settings
from .autocomplete import SmartAutocompleteJsonView
from .settings import get_bookmarks, get_setting_lazy
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


def page():
    def action_decorator(func):
        def _inner(modeladmin, request, *args, **kwargs):
            ret = func(modeladmin, request, *args, **kwargs)
            return ret
        _inner.is_page = True
        return _inner

    return action_decorator


class SmartAdminSite(AdminSite):
    sysinfo_url = False
    index_template = 'admin/index.html'
    site_title = get_setting_lazy('TITLE')
    site_header = get_setting_lazy('HEADER')
    panels = []

    def __init__(self, name='admin'):
        self.console_panels = []
        for func in self.panels:
            self.register_panel(func)
        super().__init__(name)

    def each_context(self, request):
        context = super().each_context(request)
        context['groups'] = dict(self._get_menu(request)[0])
        context['sysinfo'] = self.sysinfo_url
        context['smart_settings'] = smart_settings
        context['enable_switch'] = smart_settings.ENABLE_SWITCH
        context['bookmarks'] = get_bookmarks(request)
        context['smart'] = self.is_smart_enabled(request)
        context['smart_sections'], context['model_to_section'] = self._get_menu(request)
        context["extra_pages"] = self.extra_pages
        context["panels"] = self.console_panels
        context["admin_site"] = self
        if smart_settings.PROFILE_LINK and request.user.is_authenticated:
            context['profile_link'] = reverse(admin_urlname(request.user._meta, 'change'),
                                              args=[request.user.pk])

        return context

    def register_panel(self, callable, url_name=None, label=None):
        if not label:
            label = getattr(callable, 'verbose_name', callable.__name__.title())
        if not url_name:
            url_name = getattr(callable, 'url_name', callable.__name__.lower())
        self.console_panels.append({"func": callable,
                                    "label": str(label), "name": str(url_name)})

    def is_smart_enabled(self, request):
        return as_bool(request.COOKIES.get('smart', "0"))

    @method_decorator(never_cache)
    def index(self, request, extra_context=None):
        if self.is_smart_enabled(request):
            return self.smart_index(request)
        else:
            return super().index(request)

    def autocomplete_view(self, request):
        return SmartAutocompleteJsonView.as_view(admin_site=self)(request)

    def app_index(self, request, app_label, extra_context=None):
        groups, __ = self._get_menu(request)
        if app_label not in groups:
            request.COOKIES['smart'] = "0"
        if self.is_smart_enabled(request):
            self.app_index_template = ['admin/%s/app_index.html' % app_label,
                                       'admin/group_index.html']
        response = super().app_index(request, app_label, extra_context)
        response.set_cookie("smart", "0")
        return response

    def smart_toggle(self, request, on_off):
        path = request.GET.get('from', request.path)
        response = HttpResponseRedirect(path)
        response.set_cookie('smart', int(as_bool(on_off)))
        return response

    def show_panel(self, func, request):
        return func(self, request)

    def console(self, request, extra_context=None):
        context = self.each_context(request)
        return TemplateResponse(request, "smart_admin/console.html", context)

    def get_urls(self):
        from django.urls import path

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)

            wrapper.admin_site = self
            return update_wrapper(wrapper, view)

        urlpatterns = [path('~groups/<str:group>/', wrap(self.smart_section), name='group_list'),
                       path('smart/<str:on_off>/', wrap(self.smart_toggle), name='smart_toggle'),
                       path("console/", wrap(self.console), name="console"),
                       ]
        for entry in self.console_panels:
            urlpatterns.append(path(f"{entry['name']}/",
                                    wrap(partial(self.show_panel, entry["func"])),
                                    name=entry["name"]))
        self.extra_pages = [("Console", reverse_lazy("admin:console"))]

        # try:
        #     if 'django_sysinfo' in settings.INSTALLED_APPS:
        #         urlpatterns += [path('~sysinfo/', wrap(self.admin_sysinfo), name='smart-sysinfo-admin'), ]
        #         self.sysinfo_url = reverse_lazy('admin:smart-sysinfo-admin')
        # except ImportError:
        #     pass
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
                fqn = '{}.{}'.format(app['app_label'], model['object_name'])
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
                         # 'label': '{app[name]} - ({model[name]})'.format(app=app, model=model),
                         'label': smart_settings.MODEL_LABEL_FORMAT.format(app=app, model=model),
                         # 'label': '{model[name]} ({app[name]})'.format(app=app, model=model),
                         # 'label': '%s - %s' % (app['name'], model['name']),
                         'model_name': str(model['name']),
                         'admin_url': model['admin_url'],
                         'perms': model['perms']})
            for __, models in groups.items():
                models.sort(key=lambda x: x['label'])
            cache.set(key1, groups, 60 * 60)
            cache.set(key2, model_to_section, 60 * 60)
        return groups, model_to_section

    def get_smart_menu(self, request, group):
        groups, __ = self._get_menu(request)
        return groups[group]

    @method_decorator(never_cache)
    def smart_section(self, request, extra_context=None, group=None):
        groups, __ = self._get_menu(request)
        section = groups[group]
        context = {
            **self.each_context(request),
            'app_list': [group],
            'section': (group, section),
            **(extra_context or {}),
        }
        return TemplateResponse(request, 'admin/group_index.html', context)

    @method_decorator(never_cache)
    def smart_index(self, request, extra_context=None):
        context = {
            **self.each_context(request),
            **(extra_context or {}),
        }
        request.current_app = self.name
        return TemplateResponse(request, 'admin/smart_index.html', context)
