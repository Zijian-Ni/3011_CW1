"""
Django settings for sportspulse project.

SportsPulse is a football match statistics and analytics API.
Built with Django 5.x and Django REST Framework for the COMP3011 module.

I chose Django because it was introduced in module lectures 6-7, and
DRF extends it with serialisation, authentication, and a browsable
API — which suits a RESTful design nicely.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# In production, set DJANGO_SECRET_KEY as an environment variable
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-dev-key-change-in-production-abc123xyz'
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'zijianni.pythonanywhere.com',
]

# Register our app and third-party packages (see Lecture 6, slide 5)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    # Project app
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sportspulse.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'sportspulse.wsgi.application'

# Using SQLite — it ships with Python and is sufficient for this
# project's scale. For larger-scale production, I'd switch to PostgreSQL.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── DRF configuration ──────────────────────────────────────
# Token auth is stateless (REST constraint #2, Lecture 3) and simple.
# Read-only access is public; writes require authentication.
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '500/hour',
        'register': '5/hour',
        'login': '20/hour',
    },
}

# ── Swagger / OpenAPI settings ─────────────────────────────
SPECTACULAR_SETTINGS = {
    'TITLE': 'SportsPulse API',
    'DESCRIPTION': (
        'A football match statistics and analytics REST API providing '
        'CRUD operations for teams, players, matches, and per-match '
        'player statistics. Includes analytical endpoints for '
        'leaderboards, team performance, head-to-head records, and '
        'season summaries.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CONTACT': {'name': 'COMP3011 Coursework'},
    'LICENSE': {'name': 'MIT'},
    'TAGS': [
        {'name': 'Auth', 'description': 'Registration and login'},
        {'name': 'Teams', 'description': 'Football team CRUD'},
        {'name': 'Players', 'description': 'Player CRUD'},
        {'name': 'Matches', 'description': 'Match record CRUD'},
        {'name': 'Statistics', 'description': 'Player match statistics CRUD'},
        {'name': 'Analytics', 'description': 'Aggregated insights'},
    ],
}
