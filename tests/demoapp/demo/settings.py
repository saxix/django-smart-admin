from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve(strict=True).parents[3]

env = environ.Env(
    DEBUG=(bool, False),
    STATIC_ROOT=(str, str(BASE_DIR / '~build' / 'static')),
    DATABASE_URL=(str, "sqlite:///smart_admin.db")
)

DEBUG = env('DEBUG')

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
                  'admin_extra_urls',

                  'smart_admin.logs',
                  'smart_admin.apps.SmartTemplateConfig',
                  'smart_admin',

                  'demo']

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
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': ['django.contrib.messages.context_processors.messages',
                                   'django.contrib.auth.context_processors.auth',
                                   "django.template.context_processors.request",
                                   ]
        },
    },
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

SMART_ADMIN_BOOKMARKS = [('GitHub', 'https://github.com/saxix/django-smart-admin'),
                         'https://github.com/saxix/django-adminactions',
                         'https://github.com/saxix/django-sysinfo',
                         'https://github.com/saxix/django-adminfilters',
                         'https://github.com/saxix/django-admin-extra-urls',
                         ]
SMART_ADMIN_BOOKMARKS_PERMISSION = None
SMART_ADMIN_PROFILE_LINK = True

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
