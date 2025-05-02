from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = 'Core'
    def ready(self):
        # Подключаем сигналы при запуске приложения
        import core.signals