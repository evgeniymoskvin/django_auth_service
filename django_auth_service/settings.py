"""
Django settings for django_auth_service project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-7nba*%s6z7qpj$lw9m_j2msr70lapv-^z(vfd$vv#p&&o3k$2k'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'oauth2_provider',

    'accounts',
    'identity',
    'login'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'identity.kerberos.middleware.KerberosAuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_auth_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_auth_service.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'c:\\temp\\db.sqlite3',
    }
}

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

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = "/media/"
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
MEDIA_ROOT = MEDIA_DIR

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}
#
# LOGIN_URL = "login"
# LOGIN_REDIRECT_URL = "/"
# LOGOUT_REDIRECT_URL = "login"

LOGIN_URL = "/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# что бы создать ключ надо выполнить python generate_rsa_key.py, перед этим необходимо
# в INSTALLED_APPS добавить oauth2_provider
# выполнить python manage.py migrate

OIDC_PRIVATE_KEY_PATH = BASE_DIR / "oidc_private_key.pem"

OAUTH2_PROVIDER = {
    'OIDC_ENABLED': True,

    'OIDC_RSA_PRIVATE_KEY': OIDC_PRIVATE_KEY_PATH.read_text(
        encoding='utf-8'
    ),

    'SCOPES': {
        'openid': 'OpenID Connect scope',
        'profile': 'User profile',
        'email': 'User email address',
    },

    'PKCE_REQUIRED': True,

    'OIDC_RESPONSE_TYPES_SUPPORTED': ['code'],
    'COMPLIANT_BCP_RFC9700_PKCE_METHOD': True,

    'OAUTH2_VALIDATOR_CLASS': 'identity.oauth_validators.CustomOAuth2Validator',
}

SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_NAME = 'testsessionid'

# SESSION_COOKIE_SECURE = True # Cookie сессии передаётся только по HTTPS.
# SESSION_COOKIE_HTTPONLY = True # Cookie недоступна из JavaScript (document.cookie). Защита от XSS-кражи сессии.
#
# CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY = False
# SESSION_COOKIE_SAMESITE = "Lax" # Cookie не отправляется при cross-site запросах (POST, iframe), но отправляется при обычном переходе по ссылке. (Возможно не надо)
#
# SESSION_COOKIE_AGE = 28800 # Время жизни сессии в секундах (8 × 3600).
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True # Сессия истекает при закрытии браузера. Работает в связке с SESSION_COOKIE_AGE: сессия живёт

# Active Directory
# Включение AD-аутентификации
AD_ENABLED = False
# 	Адрес контроллера домена
AD_SERVER = None
# Имя домена
AD_DOMAIN = None
# 	Корневой DN для поиска пользователей
AD_BASE_DN = None
# 	Использовать LDAPS
AD_USE_SSL = True
# 	Таймаут подключения
AD_CONNECT_TIMEOUT = 5
# 	Таймаут ответа
AD_RECEIVE_TIMEOUT = 5

# Example
# AD_ENABLED = True
# AD_SERVER = "dc01.company.local"
# AD_DOMAIN = "company.local"
# AD_BASE_DN = "DC=company,DC=local"
# AD_USE_SSL = True
# AD_CONNECT_TIMEOUT = 5
# AD_RECEIVE_TIMEOUT = 5


# Настройки Kerberos-аутентификации
KERBEROS_ENABLED = False
# Домен Active Directory и Kerberos Realm
KERBEROS_ALLOWED_REALMS = [
    "EL-SPB.LOCAL",
]
# SPN сервиса Auth Service
KERBEROS_SERVICE_PRINCIPAL = (
    "HTTP/auth.el-spb.local@EL-SPB.LOCAL"
)
# Путь к keytab внутри Docker-контейнера
KERBEROS_KEYTAB = "/run/secrets/auth_service.keytab"
# Разрешённый механизм аутентификации
KERBEROS_ALLOWED_MECHANISM = "kerberos"
