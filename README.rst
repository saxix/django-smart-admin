django-smart-admin
==================

SmartAdmin is a set of small Django Admin utilities that aims
to remove some of the common annoying configuration issues:

It is not intended to be a fully replacement of the official Admin,
but only offers a set of mixin/utilities the often (at least for me)
need to be copy/paste in each project.


Bonus
-----
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


Demo is available at https://django-smart-admin.herokuapp.com/.
(Any user/password combination is accepted)

Components
----------
ModelAdmin Mixins
~~~~~~~~~~~~~~~~~
 - LinkedObjectsMixin
 - ReadOnlyMixin
 - FieldsetMixin
 - DisplayAllMixin



Install
-------

.. code-block::

    pip install django-smart-admin

or (if you want to install extra admin features)

.. code-block::

    pip install django-smart-admin[full]


In your `settings.py`

.. code-block::

   INSTALLED_APPS = [
       # "django.contrib.admin",  # removes standard django admin
      'django_sysinfo',  # optional
      'adminactions',  # optional
      'adminfilters',  # optional
      'admin_extra_urls', # optional

      'smart_admin.apps.SmartLogsConfig',  # optional:  log application
      'smart_admin.apps.SmartTemplateConfig',  # templates
      'smart_admin.apps.SmartAuthConfig', # optional: django.contrib.auth enhancements
      'smart_admin',
      .....
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


In your `urls.py`

.. code-block::

    import adminactions.actions as actions
    from django.contrib.admin import site

    admin.autodiscover()
    actions.add_to_site(site)

    urlpatterns = [
        ....
        path('adminactions/', include('adminactions.urls')),
    ]


Links
~~~~~

+--------------------+----------------+--------------+-----------------------------+
| Stable             | |master-build| | |master-cov| |                             |
+--------------------+----------------+--------------+-----------------------------+
| Development        | |dev-build|    | |dev-cov|    |                             |
+--------------------+----------------+--------------+-----------------------------+
| Project home page: |https://github.com/saxix/django-smart-admin                  |
+--------------------+---------------+---------------------------------------------+
| Issue tracker:     |https://github.com/saxix/django-smart-admin/issues?sort      |
+--------------------+---------------+---------------------------------------------+
| Download:          |http://pypi.python.org/pypi/django-smart-admin/              |
+--------------------+---------------+---------------------------------------------+


.. |master-build| image:: https://secure.travis-ci.com/saxix/django-smart-admin.png?branch=master
                    :target: http://travis-ci.com/saxix/django-smart-admin/

.. |master-cov| image:: https://codecov.io/gh/saxix/django-smart-admin/branch/master/graph/badge.svg
                    :target: https://codecov.io/gh/saxix/django-smart-admin

.. |dev-build| image:: https://secure.travis-ci.com/saxix/django-smart-admin.png?branch=develop
                  :target: http://travis-ci.com/saxix/django-smart-admin/

.. |dev-cov| image:: https://codecov.io/gh/saxix/django-smart-admin/branch/develop/graph/badge.svg
                    :target: https://codecov.io/gh/saxix/django-smart-admin


.. |python| image:: https://img.shields.io/pypi/pyversions/admin-extra-urls.svg
    :target: https://pypi.python.org/pypi/admin-extra-urls/
    :alt: Supported Python versions

.. |pypi| image:: https://img.shields.io/pypi/v/admin-extra-urls.svg?label=version
    :target: https://pypi.python.org/pypi/admin-extra-urls/
    :alt: Latest Version

.. |license| image:: https://img.shields.io/pypi/l/admin-extra-urls.svg
    :target: https://pypi.python.org/pypi/admin-extra-urls/
    :alt: License

.. |travis| image:: https://travis-ci.org/saxix/django-smart-admin.svg?branch=develop
    :target: https://travis-ci.com/saxix/django-smart-admin

.. |django| image:: https://img.shields.io/badge/Django-1.8-orange.svg
    :target: http://djangoproject.com/
    :alt: Django 1.7, 1.8
