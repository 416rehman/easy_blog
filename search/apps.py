try:
    from django.apps import AppConfig

    class Config(AppConfig):
        """Config."""

        name = 'search'
        label = 'search'

    __all__ = ('Config',)

except ImportError:
    pass