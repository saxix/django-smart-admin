import adminactions.actions as actions
from django.contrib import admin
from django.contrib.admin import site
from django.urls import include, path

admin.autodiscover()
actions.add_to_site(site)

urlpatterns = [
    path('', admin.site.urls),
    path('adminactions/', include('adminactions.urls')),
]


def get_link(request):
    return get_link.LINKS


get_link.LINKS = (['github', 'https://github.com', 'icon'], ['github', 'https://github.com'], ['https:///github.com'])


def get_sysinfo_key(request):
    return 'key1'
