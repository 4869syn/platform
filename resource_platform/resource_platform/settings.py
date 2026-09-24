import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-dev-key-change-in-production-2026'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'resource_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'resource_platform.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 认证配置
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# ==================== 日志配置 ====================
import logging

# 日志目录
LOG_DIR = BASE_DIR / 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] [{levelname}] [{name}] {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{asctime}] [{levelname}] {message}',
            'style': '{',
        },
        'request': {
            'format': '[{asctime}] [{levelname}] [{name}] {message}\n  Request: {request}',
            'style': '{',
        },
    },
    'handlers': {
        # 控制台输出
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'INFO',
        },
        # 所有日志文件
        'file_all': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'all.log',
            'maxBytes': 1 * 1024 * 1024,  # 5MB
            'backupCount': 3,
            'formatter': 'verbose',
            'encoding': 'utf-8',
            'level': 'INFO',
        },
        # 错误日志文件（WARNING 及以上）
        'file_error': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'error.log',
            'maxBytes': 1 * 1024 * 1024,  # 5MB
            'backupCount': 3,
            'formatter': 'verbose',
            'encoding': 'utf-8',
            'level': 'WARNING',
        },
        # 请求日志文件
        'file_request': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'request.log',
            'maxBytes': 1 * 1024 * 1024,  # 5MB
            'backupCount': 3,
            'formatter': 'request',
            'encoding': 'utf-8',
            'level': 'WARNING',
        },
    },
    'loggers': {
        # Django 请求日志（含 4xx/5xx 错误）
        'django.request': {
            'handlers': ['console', 'file_request', 'file_error'],
            'level': 'WARNING',
            'propagate': False,
        },
        # Django 服务器日志
        'django.server': {
            'handlers': ['console', 'file_request'],
            'level': 'WARNING',
            'propagate': False,
        },
        # Django 安全相关日志
        'django.security': {
            'handlers': ['console', 'file_error'],
            'level': 'WARNING',
            'propagate': False,
        },
        # Django 数据库日志
        'django.db.backends': {
            'handlers': ['file_all'],
            'level': 'WARNING',
            'propagate': False,
        },
        # Django 模板日志
        'django.template': {
            'handlers': ['console', 'file_error'],
            'level': 'WARNING',
            'propagate': False,
        },
        # 根日志（捕获所有未配置的日志）
        '': {
            'handlers': ['console', 'file_all', 'file_error'],
            'level': 'INFO',
        },
    },
}
