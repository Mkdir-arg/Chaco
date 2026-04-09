from django.apps import AppConfig


class ConversacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'conversaciones'

    def ready(self):
        import conversaciones.signals  # noqa: F401
        import conversaciones.signals_alertas

    verbose_name = 'Conversaciones'
