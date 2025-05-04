import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
APPEND_SLASH = True

# DEBUG и хосты
DEBUG = True  # Меняйте на False в production
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '10.0.100.12', 'simplepharm.pixode.ru']

# Для production: собирать статику один раз и отдавать уже с хешами в именах
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Доверенные источники для CSRF-проверки (Django ≥4.0)
CSRF_TRUSTED_ORIGINS = [
    'https://simplepharm.pixode.ru',
    'http://simplepharm.pixode.ru',
]

# Указываем Django, где находится корневой urls.py
ROOT_URLCONF = 'steroid_plan.urls'

# Безопасность: в production вытаскивайте из переменных окружения!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '@5%v122utehqzb8_p36p$i=9!$z8z11%4=ad3x__c-jwom51$3')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',

    'frontend',
    'core.apps.CoreConfig',
    'simple_history',
]

# Уникальные ключи
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Кастомная модель пользователя
AUTH_USER_MODEL = 'core.User'

# Подключение к базе данных PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'steroid_plan_db',         # имя вашей БД
        'USER': 'steroid_plan_user',                 # пользователь БД
        'PASSWORD': 'A1pY?J2b£>)1;9Yk1E',         # пароль
        'HOST': '10.0.100.14',               # или адрес сервера
        'PORT': '5432',                    # порт
    }
}




# Таймзона и статика
TIME_ZONE = 'Europe/Moscow'
USE_TZ = True
# URL для доступа к статическим файлам
STATIC_URL = '/static/'

# Папки, где Django ищет статические файлы (например, в папке проекта или приложений)
STATICFILES_DIRS = [
    BASE_DIR / "frontend" / "static",  # Папка frontend/static
]

# Папка, куда будут собираться статические файлы для продакшена
STATIC_ROOT = BASE_DIR / "staticfiles"

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

# Templates (для админки и других страниц)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # здесь можно добавить пути к пользовательским шаблонам
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


from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/calculator/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

}