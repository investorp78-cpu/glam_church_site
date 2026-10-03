import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'glam-church-fallback-key-2026')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://glam-church-site.onrender.com',
    'https://*.onrender.com',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://glafa.org',
    'https://glafa.org',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    # 'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'cloudinary',
    'core',

]

SITE_ID = 1

# ── Cloudinary ──────────────────────────────────────────────────────────
# Accepts EITHER the three separate variables OR the single CLOUDINARY_URL
# that Cloudinary shows on its dashboard (cloudinary://KEY:SECRET@CLOUDNAME).
# Values are cleaned because stray spaces/quotes from copy-paste are the most
# common reason Cloudinary rejects valid keys.
import logging
from urllib.parse import urlparse

def _clean(v):
    return (v or '').strip().strip('"').strip("'").strip()

CLOUDINARY_CLOUD_NAME = _clean(os.environ.get('CLOUDINARY_CLOUD_NAME'))
CLOUDINARY_API_KEY    = _clean(os.environ.get('CLOUDINARY_API_KEY'))
CLOUDINARY_API_SECRET = _clean(os.environ.get('CLOUDINARY_API_SECRET'))

_cloud_url = _clean(os.environ.get('CLOUDINARY_URL'))
if _cloud_url and not (CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET):
    _u = urlparse(_cloud_url)
    CLOUDINARY_CLOUD_NAME = CLOUDINARY_CLOUD_NAME or (_u.hostname or '')
    CLOUDINARY_API_KEY    = CLOUDINARY_API_KEY    or (_u.username or '')
    CLOUDINARY_API_SECRET = CLOUDINARY_API_SECRET or (_u.password or '')

# Use one source of truth, so the Cloudinary SDK never sees two configs.
os.environ.pop('CLOUDINARY_URL', None)

USING_CLOUDINARY = bool(CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET)

if USING_CLOUDINARY:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
        'API_KEY':    CLOUDINARY_API_KEY,
        'API_SECRET': CLOUDINARY_API_SECRET,
    }
    import cloudinary
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True,
    )
    # Every ImageField upload (admin "Choose file", member photos, testimony
    # photos) now goes to Cloudinary instead of the server's temporary disk.
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    logging.getLogger(__name__).warning(
        'CLOUDINARY credentials NOT found (need CLOUDINARY_CLOUD_NAME, '
        'CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET). Uploads will be saved to '
        'local disk and LOST on the next deploy/restart.'
    )

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'church_site.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'church_site.wsgi.application'

# Use PostgreSQL on Render (set DATABASE_URL env var), fallback to SQLite locally
import dj_database_url

DATABASE_URL = os.environ.get('DATABASE_URL', '')

if DATABASE_URL:
    # Ensure SSL is always required (needed for Neon free tier)
    if 'sslmode' not in DATABASE_URL:
        sep = '&' if '?' in DATABASE_URL else '?'
        DATABASE_URL = DATABASE_URL + sep + 'sslmode=require'

    _db_config = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=60,
        conn_health_checks=True,
    )
    _db_config.setdefault('OPTIONS', {})
    _db_config['OPTIONS'].update({
        'sslmode':           'require',
        'connect_timeout':   10,
        'keepalives':        1,
        'keepalives_idle':   30,
        'keepalives_interval': 10,
        'keepalives_count':  5,
    })
    DATABASES = {'default': _db_config}

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Use simplest possible static files storage — no manifest, no hashing
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Fountain of Grace Church <no-reply@fountainofgrace.org>'
