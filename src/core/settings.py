from pathlib import Path
import os

from split_settings.tools import include

BASE_DIR = Path(__file__).resolve().parent.parent
PARENT_DIR = Path(__file__).resolve().parent.parent.parent

# Environment-based settings
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-^ra6y%-&v)a4+_libik0m(f80o(u)$3+$_g%vohytz3hu_*s62')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ROOT_URLCONF = 'core.urls'

WSGI_APPLICATION = 'core.wsgi.application'

# Database configuration
if ENVIRONMENT == 'production':
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': PARENT_DIR / 'database.sqlite3',
        }
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Include component settings
include("components/*.py")

# Include production settings if in production
if ENVIRONMENT == 'production':
    from .components.production import *