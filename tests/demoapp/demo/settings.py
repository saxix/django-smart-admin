from pathlib import Path
from uuid import uuid4

import environ
from adminactions import consts
from django.utils.safestring import mark_safe

import smart_admin

BASE_DIR = Path(__file__).resolve(strict=True).parents[3]

env = environ.Env(
    DEBUG=(bool, False),
    STATIC_ROOT=(str, str(BASE_DIR / '~build' / 'static')),
    DATABASE_URL=(str, "sqlite:///smart_admin.db"),
    ROOT_TOKEN=(str, uuid4().hex),
)

DEBUG = env('DEBUG')
USE_TZ = False
STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT')
SITE_ID = 1
ROOT_URLCONF = 'demo.urls'
SECRET_KEY = 'abc'
ALLOWED_HOSTS = ['*']
AUTHENTICATION_BACKENDS = ('demo.backends.AnyUserAuthBackend',
                           )

INSTALLED_APPS = ['django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.sites',
                  'django.contrib.messages',
                  'django.contrib.staticfiles',

                  'constance',
                  'django_sysinfo',
                  'adminactions',
                  'adminfilters',
                  'adminfilters.depot',
                  'admin_extra_buttons',

                  'smart_admin.apps.SmartLogsConfig',
                  'smart_admin.apps.SmartTemplateConfig',
                  'smart_admin.apps.SmartAuthConfig',
                  'smart_admin.apps.SmartConfig',

                  'demo.apps.Config']

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
)

DATABASES = {
    'default': env.db()
}

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR / 'tests' / 'demoapp' / 'demo' / 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': ['django.contrib.messages.context_processors.messages',
                                   'django.contrib.auth.context_processors.auth',
                                   "django.template.context_processors.request",
                                   ]
        },
    },
]

SMART_ADMIN_TITLE = 'Django Admin Site'
SMART_ADMIN_HEADER = 'Django Smart Admin ' + smart_admin.VERSION

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


def get_bookmarks(request):
    return [mark_safe('<li><a target="{0}" class="viewlink" href="{1}">{0}</a></li>'.format(*e)) for e in
            [('GitHub', 'https://github.com/saxix/django-smart-admin'),
             ('PyPI', 'https://pypi.org/project/django-smart-admin/'),
             ('adminactions', 'https://github.com/saxix/django-adminactions'),
             ('sysinfo', 'https://github.com/saxix/django-sysinfo'),
             ('adminfilters', 'https://github.com/saxix/django-adminfilters'),
             ('admin-extra-urls,', 'https://github.com/saxix/django-admin-extra-urls'),
             ]]


SMART_ADMIN_BOOKMARKS = get_bookmarks
SMART_ADMIN_BOOKMARKS_PERMISSION = None
SMART_ADMIN_PROFILE_LINK = True
SMART_ADMIN_ISROOT = lambda r, *a: r.user.is_superuser and r.headers.get("x-root-token") == env('ROOT_TOKEN')

CONSTANCE_CONFIG = {
    'SITE_NAME': ('My Title', 'Website title'),
    'SITE_DESCRIPTION': ('', 'Website description'),
    'THEME': ('light-blue', 'Website theme'),
}

CONSTANCE_CONFIG_FIELDSETS = {
    'General Options': {
        'fields': ('SITE_NAME', 'SITE_DESCRIPTION'),
        'collapse': True
    },
    'Theme Options': ('THEME',),
}
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
AA_PERMISSION_HANDLER = consts.AA_PERMISSION_CREATE_USE_COMMAND
