import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = os.getenv("DJANGO_DEBUG", "0") == "1"
SESSION_COOKIE_SECURE = False  # True за прокси/HTTPS
CSRF_COOKIE_SECURE = False     # True за прокси/HTTPS
CSRF_TRUSTED_ORIGINS = ["http://localhost:8003", "http://127.0.0.1:8003"]
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "movies",
    "accounts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "admin_db"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
        "HOST": os.getenv("DB_HOST", "postgres_auth"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# === SSO/JWT settings ===

AUTH_JWKS_URL = os.getenv(
    "AUTH_JWKS_URL",
    "http://auth_service:8000/api/v1/auth/.well-known/jwks.json",
)

# Кого пускаем в админку через SSO (email whitelist, запятая-разделитель)
ALLOWED_ADMIN_EMAILS = {
    e.strip().lower()
    for e in os.getenv("ALLOWED_ADMIN_EMAILS", "admin@example.com").split(",")
    if e.strip()
}

# === Redis cache (django-redis) ===
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{os.getenv('REDIS_HOST', 'redis_shared')}"
                    f":{os.getenv('REDIS_PORT', '6379')}/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "TIMEOUT": 600,  # 10 минут по умолчанию
    }
}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = BASE_DIR / 'staticfiles'

MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# JWKS
AUTH_JWKS_URL = os.getenv(
    "AUTH_JWKS_URL",
    "http://auth_service:8000/api/v1/auth/.well-known/jwks.json")

ADMIN_SUPERUSERS = set(x.strip() for
                       x in os.getenv("ADMIN_SUPERUSERS", "")
                       .split(",") if x.strip())

AUTH_ISS = os.getenv("AUTH_ISS")  # например: http://auth_service:8000

ALLOWED_ADMIN_EMAILS = set(
    e.strip().lower() for e in os.getenv(
        "ALLOWED_ADMIN_EMAILS", "admin@example.com").
    split(",") if e.strip())
