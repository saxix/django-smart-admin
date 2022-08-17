try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os.path

here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.md')
with open(readme_path, 'rb') as stream:
    readme = stream.read().decode('utf8')

setup(
    long_description=readme,
    long_description_content_type='text/markdown',
    name='django-smart-admin',
    version='2.2.1',
    python_requires='==3.*,>=3.8',
    project_urls={"homepage": "https://github.com/saxix/django-smart-admin",
                  "repository": "https://github.com/saxix/django-smart-admin"
                  },
    author='sax',
    author_email='s.apostolico@gmail.com',
    keywords='django',
    packages=['smart_admin',
              'smart_admin.console',
              'smart_admin.logs',
              'smart_admin.smart_auth',
              'smart_admin.templatetags'],
    package_dir={"": "src"},
    package_data={"smart_admin": ["templates/**/*.html",
                                  "static/**/*.*",
                                  ]},
    extras_require={
        'full': ["django-adminfilters>=2",
                 "django-admin-extra-buttons",
                 "django-adminactions>=1.14",
                 "django-sysinfo>=2.6.2",
                 ],
        'dev': ['django-webtest',
                'django-environ',
                'whitenoise',
                'factory_boy',
                'django-constance',
                'django-picklefield',
                'bump2version',
                'factory-boy',
                'psycopg2',
                'tox',
                'flake8',
                'isort',
                'pytest',
                'pyquery',
                'pytest-echo',
                'pytest-cov',
                'pytest-django',
                'pytest-pythonpath',
                ]
    },
)
