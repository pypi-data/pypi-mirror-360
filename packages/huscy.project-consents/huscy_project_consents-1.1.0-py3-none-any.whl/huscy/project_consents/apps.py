from django.apps import AppConfig


class HuscyApp(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'huscy.project_consents'

    class HuscyAppMeta:
        pass
