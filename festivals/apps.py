from django.apps import AppConfig


class FestivalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'festivals'

    def ready(self):
        import festivals.signals # signals 등록