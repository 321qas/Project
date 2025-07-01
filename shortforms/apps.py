from django.apps import AppConfig


class ShortformsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shortforms'

    def ready(self):
        # signals.py를 import해서 시그널 연결!
        import shortforms.signals