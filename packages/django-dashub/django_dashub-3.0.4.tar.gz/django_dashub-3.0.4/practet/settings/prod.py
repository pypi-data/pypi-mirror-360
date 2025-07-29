from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qle%9=&^4)21c0ntbmmm(e6-pmfqwm0@w166yqf%@%!uggpzqd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_ROOT = BASE_DIR / "media"

#Security Settings
SECURE_HSTS_SECONDS = 3600
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CELERY CONFIGURATION
CELERY_BROKER_URL = "amqp://guest:guest@localhost:5672/"

# CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    "https://admin.practet.com"
]
