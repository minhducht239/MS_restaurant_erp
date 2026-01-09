import os
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-staff-service-key')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'django_filters',
    'staff',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'staff_service.urls'
WSGI_APPLICATION = 'staff_service.wsgi.application'

# Parse DATABASE_URL for DigitalOcean managed database
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL:
    parsed = urlparse(DATABASE_URL)
    DB_NAME = parsed.path.lstrip('/')
    DB_USER = parsed.username or 'root'
    DB_PASSWORD = parsed.password or ''
    DB_HOST = parsed.hostname or 'localhost'
    DB_PORT = str(parsed.port or 3306)
else:
    DB_NAME = os.environ.get('DB_NAME', 'defaultdb')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')

DATABASES = {'default': {'ENGINE': 'django.db.backends.mysql', 'NAME': DB_NAME, 'USER': DB_USER, 'PASSWORD': DB_PASSWORD, 'HOST': DB_HOST, 'PORT': DB_PORT, 'OPTIONS': {'charset': 'utf8mb4', 'ssl': {'ca': '/etc/ssl/certs/ca-certificates.crt'} if not DEBUG else {}}}}

REST_FRAMEWORK = {'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'], 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination', 'PAGE_SIZE': 20}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }
]


