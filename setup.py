from setuptools import setup, find_packages

import os.path

here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.md')
with open(readme_path, 'rb') as stream:
    readme = stream.read().decode('utf8')

setup(
    long_description=readme,
    long_description_content_type='text/markdown',
    name='django-smart-admin',
    version='2.6.0',
    python_requires='==3.*,>=3.8',
    url="https://github.com/saxix/django-smart-admin",
    project_urls={"homepage": "https://github.com/saxix/django-smart-admin",
                  "repository": "https://github.com/saxix/django-smart-admin"
                  },
    author='sax',
    author_email='s.apostolico@gmail.com',
    keywords='django',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=["django-adminfilters>=2",
                      "django-admin-extra-buttons",
                      "django-adminactions>=1.14",
                      "django-sysinfo>=2.6.2",
                      ],
    extras_require={
        'full': [],
        'dev': [
            'django<4',
            'bump2version',
            'celery',
            'django-constance',
            'django-environ',
            'django-picklefield',
            'django-webtest',
            'factory-boy',
            'flake8',
            'isort',
            'psycopg2<=2.8',
            'pyquery',
            'pytest-cov',
            'pytest-django',
            'pytest-echo',
            'pytest-pythonpath',
            'pytest<7',
            'responses',
            'sentry_sdk<1.22',
            'tox',
            'whitenoise',
            ]
    },
)
