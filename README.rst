django-smart-admin
==================

SmartAdmin is a set of small Django Admin utilities that aims 
to remove some of the common annoying configuration issues:

Install
=======

Simply comment ``django.contrib.admin`` in your ``INSTALLED_APPS`` and add ``smart_admin``

.. code-block::

   INSTALLED_APPS = [
       # "django.contrib.admin",
       "smart_admin.template",
       "smart_admin",
       .....
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
