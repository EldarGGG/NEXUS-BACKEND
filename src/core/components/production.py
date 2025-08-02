import os

# Production settings for Railway deployment
try:
    import dj_database_url
except ImportError:
    dj_database_url = None

# Security settings
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-^ra6y%-&v)a4+_libik0m(f80o(u)$3+$_g%vohytz3hu_*s62')

# Database configuration for Railway PostgreSQL
if dj_database_url and os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # Fallback to SQLite for development
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'database.sqlite3',
        }
    }

# Allowed hosts for Railway
ALLOWED_HOSTS = [
    '.railway.app',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]

# CORS settings for production
CORS_ALLOWED_ORIGINS = [
    "https://nexus-platform.vercel.app",
    "https://nexus-market.vercel.app",
    "http://localhost:3000",
    "http://localhost:3002",
]

CORS_ALLOW_CREDENTIALS = True

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    "https://nexus-platform.vercel.app",
    "https://nexus-market.vercel.app",
    "https://*.railway.app",
]

# Static files settings for Railway
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'staticfiles')

# Media files settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'media')

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
