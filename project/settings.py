# -*- coding: utf-8 -*-
# Django settings for DPNK project.
import os
import sys

normpath = lambda *args: os.path.normpath(os.path.abspath(os.path.join(*args)))
PROJECT_ROOT = normpath(__file__, "..", "..")

sys.path.append(normpath(PROJECT_ROOT, "project"))
sys.path.append(normpath(PROJECT_ROOT, "apps"))

DEBUG = True
ADMINS = (
    ('Hynek Hanke', 'hynek.hanke@auto-mat.cz'),
#    ('Vaclav Rehak', 'vrehak@baf.cz'),
#    ('Petr Studený', 'petr.studeny@auto-mat.cz'),
)
DEFAULT_FROM_EMAIL = 'Do práce na kole <kontakt@dopracenakole.net>'
MANAGERS = ADMINS
DATABASES = {
        'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': '',
                'USER': '',
                'PASSWORD': '',
                'HOST': 'localhost',
                'PORT': '',
                'OPTIONS': { 'init_command': 'SET storage_engine=INNODB,character_set_connection=utf8,collation_connection=utf8_unicode_ci' }
        },
}
LOCALE_PATH = normpath(PROJECT_ROOT, 'dpnk/locale')
TIME_ZONE = 'Europe/Prague'
LANGUAGE_CODE = 'cs-CZ'
SITE_ID = 5
USE_I18N = True
MEDIA_ROOT = normpath(PROJECT_ROOT, 'static/upload')
MEDIA_URL = '/upload/'
STATIC_ROOT = normpath(PROJECT_ROOT, "static/static")
STATIC_URL = '/media/'  # XXX: possible depences, rename static
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
SECRET_KEY = ''
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
)
ROOT_URLCONF = 'urls'
TEMPLATE_DIRS = (
    normpath(PROJECT_ROOT, 'templates'),
)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.staticfiles',

    'registration',
    'dpnk',
    'smart_selects',
    'composite_field',
    'south',
)
AUTH_PROFILE_MODULE = 'dpnk.UserProfile'
SERVER_EMAIL='root@auto-mat.cz'
LOGIN_URL = '/registrace/login/'
LOGIN_REDIRECT_URL = '/registrace/profil/'
SITE_URL = ''
COMPETITION_STATE='not_started_yet'
#COMPETITION_STATE='started'