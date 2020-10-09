import django, sys, os
from django.conf import settings

SECRET_KEY = '--'
BASE_DIR = os.path.dirname(__file__)

FIXTURE_DIRS = [os.path.join(BASE_DIR, 'tests', 'fixtures')]

DEBUG=True

DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(__file__), 'db.sqlite3'),
    }
}

INSTALLED_APPS=(
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_loopback_js_filters',

    'tests'
)
