import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env(path):
    """Lee KEY=VALUE de backend/.env sin depender de paquetes extra."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


# ENV_FILE permite usar otra configuración sin tocar .env,
# ej. PowerShell:  $env:ENV_FILE=".env.neon"; python manage.py migrate
_load_env(BASE_DIR / os.environ.get("ENV_FILE", ".env"))

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insegura-solo-local" if DEBUG else "")
if not SECRET_KEY:
    raise RuntimeError("Falta DJANGO_SECRET_KEY (obligatoria con DJANGO_DEBUG=0)")

# En local los celulares entran por la IP de la PC; en Render: DJANGO_ALLOWED_HOSTS=.onrender.com
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

# Para el panel /admin detrás de HTTPS (Render): ej. https://yape-voz-backend.onrender.com
CSRF_TRUSTED_ORIGINS = [
    o for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o
]
# Render termina el HTTPS en su proxy y reenvía por HTTP con este header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "daphne",  # debe ir primero: hace que runserver sirva también WebSockets
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "channels",
    "corsheaders",
    "yape",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # debe ir antes de CommonMiddleware
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # sirve el CSS del /admin en producción
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "yape_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "yape_backend.wsgi.application"
ASGI_APPLICATION = "yape_backend.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "yape_voz"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        # Neon (nube) exige SSL; el PostgreSQL local no.
        "OPTIONS": {"sslmode": os.environ.get("DB_SSLMODE", "prefer")},
        # Reusa conexiones: con una BD remota abrir una por request es lento.
        "CONN_MAX_AGE": 60,
        "CONN_HEALTH_CHECKS": True,
    }
}

# Un solo proceso (local y servidor pequeño): basta la capa en memoria.
# Si algún día se corren varios procesos, cambiar a channels_redis.
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

# La app Flutter en el navegador (flutter run -d chrome) corre en otro puerto/origen.
# La API usa token (no cookies), así que permitir cualquier origen no expone sesiones.
CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # python manage.py collectstatic (en el build de Render)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"yape": {"handlers": ["console"], "level": "INFO"}},
}
