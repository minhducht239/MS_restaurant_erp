"""
Base settings shared across all microservices
"""
import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


def get_base_settings():
    """Return base settings dict for all microservices"""
    return {
        # Security
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'django-insecure-default-key'),
        'DEBUG': os.environ.get('DEBUG', 'False').lower() == 'true',
        'ALLOWED_HOSTS': ['*'],
        
        # Database
        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': os.environ.get('DB_NAME', 'restaurant_erp'),
                'USER': os.environ.get('DB_USER', 'root'),
                'PASSWORD': os.environ.get('DB_PASSWORD', ''),
                'HOST': os.environ.get('DB_HOST', 'localhost'),
                'PORT': os.environ.get('DB_PORT', '3306'),
                'OPTIONS': {
                    'charset': 'utf8mb4',
                    'use_unicode': True,
                },
            }
        },
        
        # Internationalization
        'LANGUAGE_CODE': 'vi',
        'TIME_ZONE': 'Asia/Ho_Chi_Minh',
        'USE_I18N': True,
        'USE_TZ': True,
        
        # Static files
        'STATIC_URL': '/static/',
        'STATIC_ROOT': BASE_DIR / 'staticfiles',
        'MEDIA_URL': '/media/',
        'MEDIA_ROOT': BASE_DIR / 'media',
        
        # REST Framework
        'REST_FRAMEWORK': {
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'shared.jwt_auth.JWTAuthentication',
                'shared.jwt_auth.ServiceAuthentication',
            ),
            'DEFAULT_PERMISSION_CLASSES': [
                'rest_framework.permissions.IsAuthenticated',
            ],
            'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
            'PAGE_SIZE': 20,
            'DEFAULT_RENDERER_CLASSES': (
                'rest_framework.renderers.JSONRenderer',
            ),
            'EXCEPTION_HANDLER': 'shared.exception_handler.custom_exception_handler',
        },
        
        # JWT Settings
        'SIMPLE_JWT': {
            'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.environ.get('JWT_ACCESS_TOKEN_LIFETIME', 60))),
            'REFRESH_TOKEN_LIFETIME': timedelta(minutes=int(os.environ.get('JWT_REFRESH_TOKEN_LIFETIME', 1440))),
            'ROTATE_REFRESH_TOKENS': True,
            'BLACKLIST_AFTER_ROTATION': True,
            'ALGORITHM': 'HS256',
            'SIGNING_KEY': os.environ.get('SECRET_KEY', 'django-insecure-default-key'),
            'AUTH_HEADER_TYPES': ('Bearer',),
        },
        
        # CORS
        'CORS_ALLOW_ALL_ORIGINS': True,
        'CORS_ALLOW_CREDENTIALS': True,
        'CORS_ALLOW_HEADERS': [
            'accept',
            'accept-encoding',
            'authorization',
            'content-type',
            'dnt',
            'origin',
            'user-agent',
            'x-csrftoken',
            'x-requested-with',
            'x-service-key',
        ],
        
        # Logging
        'LOGGING': {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                    'style': '{',
                },
                'simple': {
                    'format': '{levelname} {message}',
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
        },
        
        # Default primary key field type
        'DEFAULT_AUTO_FIELD': 'django.db.models.BigAutoField',
    }


# Common installed apps for all services
COMMON_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'rest_framework',
    'corsheaders',
    'django_filters',
]

# Common middleware
COMMON_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]
