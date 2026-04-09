from django.apps import AppConfig


class LegajosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'legajos'
    verbose_name = 'Legajos'
    
    def ready(self):
        import legajos.signals  # noqa: F401
        import legajos.signals.alerts  # noqa: F401
        import legajos.signals.historial  # noqa: F401
        import legajos.signals.programas  # noqa: F401
        import legajos.signals.nachec  # noqa: F401
