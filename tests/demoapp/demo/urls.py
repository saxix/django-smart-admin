from django.contrib import admin
from django.contrib.admin import site
from django.urls import path, include
import adminactions.actions as actions

admin.autodiscover()
actions.add_to_site(site)

urlpatterns = [
    path('', admin.site.urls),
    path('adminactions/', include('adminactions.urls')),
]
