
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# The SECRET_KEY is provided via an environment variable in OpenShift
SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    # safe value used for development when DJANGO_SECRET_KEY might not be set
    '9e4@&tw46$l31)zrqe3wi+-slqm(ruvz&se0^%9#6(_w3ui!c0'
)

#setup DEBUG based on the DJANGO_SECRET_KEY in the environment
ON_PAAS = 'DJANGO_SECRET_KEY' in os.environ
WWWNAME = ['www.stocksonthebeach.com','stocksonthebeach.com']
DEBUG = not ON_PAAS
DEBUG = DEBUG or 'DEBUG' in os.environ

#if ON_PAAS:
#    ALLOWED_HOSTS = [os.environ['OPENSHIFT_APP_DNS'], socket.gethostname()] + WWWNAME
#else:
ALLOWED_HOSTS = ['*']

#django-allauth
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
   'allauth.account.auth_backends.AuthenticationBackend',
)

# Application definition

INSTALLED_APPS = (
    'aim',
    'loader', 
    'alerter',

    'django.contrib.auth',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',

    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'users',
    )

# AUTH_USER_MODEL = 'users.User'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
)

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

from . import database

DATABASES = {
    'default': database.config()
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

#django-allauth
SITE_ID = 1

# FTP information
FTPLOGIN = os.getenv("FTPLOGIN", None)
FTPPASS  = os.getenv("FTPPASS", None)

# EMAIL settings
ADMINS = ( ('John', 'john@compunique.com'),)

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_USER", None)
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD", None) 
