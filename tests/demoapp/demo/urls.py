import django_sysinfo.urls
from django.contrib import admin
from django.contrib.admin import site
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
import adminactions.actions as actions

admin.autodiscover()
actions.add_to_site(site)

urlpatterns = [
    path(r'', admin.site.urls),
    path(r'', include(django_sysinfo.urls)),
    path(r'adminactions/', include('adminactions.urls')),

]
