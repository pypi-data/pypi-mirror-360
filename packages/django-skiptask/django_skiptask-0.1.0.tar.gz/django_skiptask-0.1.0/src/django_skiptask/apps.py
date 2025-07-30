from django.apps import AppConfig


class SkiptaskConfig(AppConfig):
    name = 'django_skiptask'
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        from . import handlers
