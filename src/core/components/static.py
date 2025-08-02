from pathlib import Path

PARENT_DIR = Path(__file__).resolve().parent.parent.parent

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    "static",
]

MEDIA_URL = '/media/'
MEDIA_ROOT = 'media/'

STATIC_ROOT = PARENT_DIR / 'static-prod/'
