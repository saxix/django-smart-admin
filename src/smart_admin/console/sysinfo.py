from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page


def panel_sysinfo(self, request):
    @cache_page(0)
    def _sysinfo(request):
        from django_sysinfo.api import get_sysinfo
        infos = get_sysinfo(request)
        infos.setdefault('extra', {})
        infos.setdefault('checks', {})
        context = self.each_context(request)
        context.update({'title': 'sysinfo',
                        'infos': infos,
                        'enable_switch': True,
                        'has_permission': True,
                        })
        return render(request,
                      'smart_admin/panels/sysinfo.html', context)

    return _sysinfo(request)


panel_sysinfo.verbose_name = _("System Info")
panel_sysinfo.url_name = "sysinfo"
