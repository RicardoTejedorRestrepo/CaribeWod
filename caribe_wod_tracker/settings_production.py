# settings_production.py
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['ricardoTejedor.pythonanywhere.com']

# Database MySQL para PythonAnywhere
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ricardoTejedor$caribe_wod',
        'USER': 'ricardoTejedor',
        'PASSWORD': 'tu_password_mysql',
        'HOST': 'ricardoTejedor.mysql.pythonanywhere-services.com',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Static files configuration
STATIC_ROOT = '/home/ricardoTejedor/caribe_wod_tracker/static'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True