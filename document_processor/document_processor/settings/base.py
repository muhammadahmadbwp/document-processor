import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'corsheaders',
    'django_celery_results',
    'django_celery_beat',
    'rest_framework',
    'django.contrib.humanize',
    'drf_yasg',
    'django_user_agents',
    'constance',
]

CUSTOM_APPS = [
    'custom_middlewares',
    'document_processor_app',
]

INSTALLED_APPS = INSTALLED_APPS + THIRD_PARTY_APPS + CUSTOM_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'custom_middlewares.RequestAndErrorHandlingMiddleware.RequestAndErrorHandling',
]

ROOT_URLCONF = 'document_processor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'document_processor.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'document_processor'),
        'USER': os.environ.get('POSTGRES_USER', 'user'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'password'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery Configuration Options
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Celery settings
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'amqp://guest:guest@rabbitmq:5672/')

# Cache settings
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://redis:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Celery beat settings
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

DEBUG_LOG_DIR = LOG_DIR / 'debug'
DEBUG_LOG_DIR.mkdir(exist_ok=True)
DEBUG_LOG_FILE = DEBUG_LOG_DIR / 'debug.log'


INFO_LOG_DIR = LOG_DIR / 'info'
INFO_LOG_DIR.mkdir(exist_ok=True)
INFO_LOG_FILE = INFO_LOG_DIR / 'info.log'

ERROR_LOG_DIR = LOG_DIR / 'error'
ERROR_LOG_DIR.mkdir(exist_ok=True)
ERROR_LOG_FILE = ERROR_LOG_DIR / 'error.log'

WARNING_LOG_DIR = LOG_DIR / 'warning'
WARNING_LOG_DIR.mkdir(exist_ok=True)
WARNING_LOG_FILE = WARNING_LOG_DIR / 'warning.log'

CRITICAL_LOG_DIR = LOG_DIR / 'critical'
CRITICAL_LOG_DIR.mkdir(exist_ok=True)
CRITICAL_LOG_FILE = CRITICAL_LOG_DIR / 'critical.log'

CELERY_LOG_DIR = LOG_DIR / 'celery'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'request_id': {
            '()': 'custom_middlewares.log_filters.RequestIDFilter',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {name} {module} {filename}:{funcName}:{lineno} [request_id:{request_id}] PID:{process:d} TID:{thread:d} {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(module)s %(filename)s %(funcName)s %(lineno)d %(request_id)s %(process)d %(thread)d %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '%'
        }
    },
    'handlers': {
        'debug_logger': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'filename': str(DEBUG_LOG_FILE),
            'interval': 1,
            'backupCount': 5,
            'formatter': 'verbose',
            'filters': ['request_id']
        },
        'info_logger': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'filename': str(INFO_LOG_FILE),
            'interval': 1,
            'backupCount': 5,
            'formatter': 'verbose',
            'filters': ['request_id']
        },
        'error_logger': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'filename': str(ERROR_LOG_FILE),
            'interval': 1,
            'backupCount': 5,
            'formatter': 'verbose',
            'filters': ['request_id']
        },
        'warning_logger': {
            'level': 'WARNING',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'filename': str(WARNING_LOG_FILE),
            'interval': 1,
            'backupCount': 5,
            'formatter': 'verbose',
            'filters': ['request_id']
        },
        'critical_logger': {
            'level': 'CRITICAL',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'filename': str(CRITICAL_LOG_FILE),
            'interval': 1,
            'backupCount': 5,
            'formatter': 'verbose',
            'filters': ['request_id']
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['request_id']
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'debug_logger', 'info_logger', 'error_logger', 'warning_logger', 'critical_logger'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'debug_logger': {
            'handlers': ['debug_logger'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'info_logger': {
            'handlers': ['info_logger'],
            'level': 'INFO',
            'propagate': False,
        },
        'error_logger': {
            'handlers': ['error_logger'],
            'level': 'ERROR',
            'propagate': False,
        },
        'warning_logger': {
            'handlers': ['warning_logger'],
            'level': 'WARNING',
            'propagate': False,
        },
        'critical_logger': {
            'handlers': ['critical_logger'],
            'level': 'CRITICAL',
            'propagate': False,
        }
    }
}