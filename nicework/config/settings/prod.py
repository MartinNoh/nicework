import os
from .base import *
from .base import BASE_DIR

SECRET_KEY = str(os.environ.get("SECRET_KEY"))

DEBUG = int(os.environ.get("DEBUG", default=0))

# 'DJANGO_ALLOWED_HOSTS' should be a single string of hosts with a space between each.
# For example: 'DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]'
ALLOWED_HOSTS = str(os.environ.get("DJANGO_ALLOWED_HOSTS")).split(" ")

DATABASES = {
    "default": {
        "ENGINE": str(os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3")),
        "NAME": str(os.environ.get("SQL_DATABASE", BASE_DIR / "db.sqlite3")),
        "USER": str(os.environ.get("SQL_USER", "user")),
        "PASSWORD": str(os.environ.get("SQL_PASSWORD", "password")),
        "HOST": str(os.environ.get("SQL_HOST", "localhost")),
        "PORT": str(os.environ.get("SQL_PORT", "5432")),
    }
}

STATIC_ROOT = BASE_DIR / "staticfiles"
# base.py에서 명시한 찾아야하는 static 폴더를 STATICFILES_DIRS = []로 override하면 collectstatic을 못함.