from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    trend_manager = None

    def ready(self):
        print('READY')
        from .trend_manager import TrendManager
        self.trend_manager = TrendManager(0.3)
        self.trend_manager.start()
