Release 2.6
-----------
* fixes `reverse_object_url()`
* updates LinkedObjectsMixin: 
  * `get_ignored_linked_objects` renamed `get_excluded_linked_objects`
  * `linked_objects_ignore` renamed `linked_objects_exclude`
  * added `linked_objects_filter`
    * `linked_objects_filter = None` display all reverse relations
    * `linked_objects_filter = []` do not display reverse relations
    * `linked_objects_filter = [a,b,...]` only display `a`,`b` reverse relations
  

Release 2.5
-----------
* add `SmartAdminSite.smart_index_template` and `SmartAdminSite.group_index_template`
* minor refactoring of `SmartAdminSite`
* fixes `LinkedObjectsMixin.linked_objects_hide_empty`
* BACKWARD INCOMPATIBLE: change signature of `get_admin_href` template tags


Release 2.4.1
-------------
* Fixes LinkedObjectsMixin


Release 2.4
-----------
* fixes compat Django 4.1


Release 2.3.1
-------------
* bug fixes


Release 2.3
-------------
* add extra panels: email, redis, error pages, sentry


Release 2.2.3
-------------
* uses setuptools
* add MANIFEST.in


Release 2.2.2
-------------
* do not set empty cookie
* Fixes packaging issue


Release 2.2.1
-------------
* Fixes packaging issue


Release 2.2
-------------
* Improves "Console" and Panels management


Release 2.1
-------------
* Fixes `TruncateAdminMixin`


Release 2.0.2
-------------
* bug fixes


Release 2.0.1
-------------
* bug fixes


Release 2.0
-----------
* enhanced LinkedObjectsMixin
* add "Console/Panels"


Release 1.9.2
-----------
* fixes LogEntryAdmin


Release 1.9.1
-----------
* bug fixes


Release 1.9
-----------
* move to  django-admin-extra-buttons
* update deps


Release 1.8
-----------
* added support to Django 4.0

