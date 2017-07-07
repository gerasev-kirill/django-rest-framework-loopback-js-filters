import django, sys, os
from django.conf import settings

BASE_DIR = os.path.dirname(__file__)
FIXTURE_DIRS = [os.path.join(BASE_DIR, 'tests', 'fixtures')]
SECRET_KEY = '--'

DEBUG=True
DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}
BASE_DIR=BASE_DIR
FIXTURE_DIRS=FIXTURE_DIRS
INSTALLED_APPS=(
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'rest_framework',
    'rest_framework.authtoken',
    'drfs_loopback_js_filters',

    'tests'
)
