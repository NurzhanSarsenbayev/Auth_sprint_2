from .settings import *

DEBUG = True
SECRET_KEY = "test-secret-key"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "admin_test",
        "USER": "test_user",
        "PASSWORD": "test_password",
        "HOST": "test_postgres",
        "PORT": 5432,
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

LANGUAGE_CODE = "en-us"

ALLOWED_ADMIN_EMAILS = ["editor@example.com", "admin@example.com"]
