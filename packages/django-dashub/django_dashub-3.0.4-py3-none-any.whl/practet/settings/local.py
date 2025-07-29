from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--!p%ec_&($k+293iog(51oem#fqi-%*%6wdfz5_1^@w*jlurhc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
USE_AWS_S3 = config("USE_AWS_S3", default=False, cast=bool)
USE_AWS_S3_STATIC = config("USE_AWS_S3_STATIC", default=False, cast=bool)
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = f"cdn.practet.com"
AWS_S3_URL = f"https://cdn.practet.com"
AWS_S3_REGION_NAME = config("AWS_REGION_NAME")
AWS_S3_FILE_OVERWRITE = True

if USE_AWS_S3:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "location": "media"
            }
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }

    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
    STATIC_ROOT = os.path.join(BASE_DIR, "public", "static")
    STATIC_URL = 'static/'
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
    MEDIA_URL = AWS_S3_URL + "/media/"
else:
    STATIC_ROOT = os.path.join(BASE_DIR, "public", "static")
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
    STATIC_URL = 'static/'
    MEDIA_URL = '/media/'

# Security Settings
CSRF_TRUSTED_ORIGINS = [
    "http://admin.example.com:8000"
]

# CELERY CONFIGURATION
CELERY_BROKER_URL = "amqp://guest:guest@localhost:5672/"
