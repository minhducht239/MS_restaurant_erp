"""Menu Service Settings"""
import os
from pathlib import Path
from datetime import timedelta
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-menu-service-key')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'django_filters',
    'menu',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'menu_service.urls'
WSGI_APPLICATION = 'menu_service.wsgi.application'

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            'ssl': {'ca': '/etc/ssl/certs/ca-certificates.crt'} if not DEBUG else {},
        },
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# S3 / DigitalOcean Spaces Configuration
USE_SPACES = os.environ.get('USE_SPACES', 'False').lower() == 'true'

# Debug logging for Spaces configuration
print(f"[MENU-SERVICE] USE_SPACES = {USE_SPACES}")
print(f"[MENU-SERVICE] USE_SPACES env = '{os.environ.get('USE_SPACES', 'NOT SET')}'")
if USE_SPACES:
    print(f"[MENU-SERVICE] AWS_STORAGE_BUCKET_NAME = {os.environ.get('AWS_STORAGE_BUCKET_NAME', 'NOT SET')}")
    print(f"[MENU-SERVICE] AWS_S3_ENDPOINT_URL = {os.environ.get('AWS_S3_ENDPOINT_URL', 'NOT SET')}")
    print(f"[MENU-SERVICE] AWS_ACCESS_KEY_ID = {'SET' if os.environ.get('AWS_ACCESS_KEY_ID') else 'NOT SET'}")

if USE_SPACES:
    # Cấu hình cho DigitalOcean Spaces
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')
    
    # Cấu hình public read (để người dùng xem được ảnh)
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_LOCATION = 'media'
    AWS_DEFAULT_ACL = 'public-read'
    
    # Sử dụng S3Boto3Storage
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "endpoint_url": AWS_S3_ENDPOINT_URL,
                "location": "media",
                "default_acl": "public-read",
                "querystring_auth": False  # Quan trọng: tắt chữ ký URL để link tồn tại lâu dài
            },
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    
    # Media URL sẽ là đường dẫn trực tiếp tới Spaces
    MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/media/'

else:
    # Cấu hình chạy Local (giữ nguyên như cũ)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# Đảm bảo MEDIA_ROOT luôn tồn tại cho các thao tác Django internal
# (cần thiết ngay cả khi sử dụng Spaces vì một số code Django vẫn reference đến nó)
if USE_SPACES:
    MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'menu': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]


