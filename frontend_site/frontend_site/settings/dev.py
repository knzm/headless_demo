from .base import *  # NOQA: F401, F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ua*iss&abyqbdy-i8%%9huh%-0-syrelyf##ox%1duo60#v-29'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


try:
    from .local import *  # NOQA: F401, F403
except ImportError:
    pass
