from django.apps import AppConfig


class CustomizingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customizing'
