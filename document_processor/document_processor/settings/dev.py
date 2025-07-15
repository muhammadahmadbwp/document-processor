from .base import *
import socket

load_dotenv(BASE_DIR / 'env/dev/.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG')

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS += [
    'debug_toolbar',
    'silk',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'silk.middleware.SilkyMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS += [ip[: ip.rfind(".")] + ".1" for ip in ips]

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True,
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # Only for development
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'authorization',
    'content-type',
    'origin',
    'user-agent',
    'x-csrftoken',
]

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
]

# CSRF settings
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000']

# Email settings (for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'