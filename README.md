django-smart-admin
==================


[![Pypi](https://badge.fury.io/py/django-smart-admin.svg)](https://badge.fury.io/py/django-smart-admin)
[![coverage](https://codecov.io/github/saxix/django-smart-admin/coverage.svg?branch=develop)](https://codecov.io/github/saxix/django-smart-admin?branch=develop)
[![Test](https://github.com/saxix/django-smart-admin/actions/workflows/test.yml/badge.svg)](https://github.com/saxix/django-smart-admin/actions/workflows/test.yml)

SmartAdmin is a set of small Django Admin utilities that aims to remove some of the common annoying configuration
issues:

It is not intended to be a fully replacement of the official Admin, but only offers a set of mixin/utilities the often (
at least for me)
need to be copied/pasted in each project.

## Bonus

- easily group models by context instead by app
- display admin logentry for any user
- display group members
- display user permissions
- display permission owners
- Display all columns ModelAdmin mixin
- log added/removed permissions for User/Group
- log added/removed groups for User
- ability to set `readonly_fields = ('__all__',)` (ReadOnlyMixin)
- display all model fields in `changelist` (DisplayAllMixin)
- automatically creates filter for each indexed field (SmartAutoFilterMixin)
- improved fieldset allows the use of `__others__` to include any field not included in others fieldsets (FieldsetMixin)
- ability to customise Autocomplete labels
- user defined "site panels"


Demo is available at https://django-smart-admin.herokuapp.com/.
(Any user/password combination is accepted)

## Components

- LinkedObjectsMixin
- ReadOnlyMixin
- FieldsetMixin
- DisplayAllMixin

## Install

    pip install django-smart-admin

or (if you want to install extra admin features)

    pip install django-smart-admin[full]

In your `settings.py`

```python

INSTALLED_APPS = [
    # "django.contrib.admin",  # removes standard django admin
    'django_sysinfo',  # optional
    'adminactions',  # optional
    'adminfilters',  # optional
    'admin_extra_buttons',  # optional

    'smart_admin.apps.SmartTemplateConfig',  # templates
    'smart_admin',  # use this instead of 'django.contrib.admin'

    'smart_admin.apps.SmartLogsConfig',  # optional:  log application
    'smart_admin.apps.SmartAuthConfig',  # optional: django.contrib.auth enhancements

]
SMART_ADMIN_SECTIONS = {
    'Demo': ['demo', ],
    'Security': ['auth',
                 'auth.User',
                 ],

    'Logs': ['admin.LogEntry',
             ],
    'Other': [],
    '_hidden_': ["sites"]
}

# add some bookmark
SMART_ADMIN_BOOKMARKS = [('GitHub', 'https://github.com/saxix/django-smart-admin')]

# no special permissions to see bookmarks
SMART_ADMIN_BOOKMARKS_PERMISSION = None

# add 'profile' link on the header
SMART_ADMIN_PROFILE_LINK = True

# display all users action log, not only logged user
SMART_ADMIN_ANYUSER_LOG = True

```

In your `urls.py`

```python

from django.contrib import admin
from django.urls import include, path
import adminactions.actions as actions
from django.contrib.admin import site

admin.autodiscover()
actions.add_to_site(site)

urlpatterns = [
    path('', admin.site.urls),
    path('adminactions/', include('adminactions.urls')),
]

```

#### Project Links

- Code: https://github.com/saxix/django-smart-admin
- PyPi: https://pypi.org/project/django-smart-admin/
