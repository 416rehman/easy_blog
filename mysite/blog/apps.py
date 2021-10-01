from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    trend_manager = None

    def ready(self):
        from .trend_manager import TrendManager
        self.trend_manager = TrendManager()
        self.trend_manager.start(0.1)
