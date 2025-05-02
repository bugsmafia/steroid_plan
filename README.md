steroid_plan/                # корень проекта
├── manage.py               # точка входа Django
├── requirements.txt        # зависимости проекта
├── README.md               # описание и инструкции по запуску
├── steroid_plan/           # пакет Django-проекта
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py         # настройки (INSTALLED_APPS, AUTH_USER_MODEL, DATABASES и т.п.)
│   ├── urls.py             # маршруты верхнего уровня
│   └── wsgi.py
└── core/                   # приложение "core"
    ├── __init__.py
    ├── admin.py           # регистрация моделей в админке
    ├── apps.py            # конфиг приложения
    ├── models.py          # модели (users, drugs и т.д.)
    ├── serializers.py     # DRF-сериализаторы
    ├── views.py           # DRF-вьюсеты или CBV
    ├── urls.py            # маршруты для core
    ├── tests.py           # модуль тестов
    └── migrations/        # миграции
        └── __init__.py