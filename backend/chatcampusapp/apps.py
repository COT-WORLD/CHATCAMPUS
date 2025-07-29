from django.apps import AppConfig


class ChatcampusappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatcampusapp'

    def ready(self):
        import chatcampusapp.signals
