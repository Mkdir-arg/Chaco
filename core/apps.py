from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        """Importa las señales de cache y auditoría cuando la app está lista."""
        import core.cache_utils  # noqa: F401, pylint: disable=import-outside-toplevel,unused-import
        import core.signals.auditoria  # noqa: F401, pylint: disable=import-outside-toplevel,unused-import
        import core.signals.auditoria_historial  # noqa: F401, pylint: disable=import-outside-toplevel,unused-import
        import core.signals.cache  # noqa: F401, pylint: disable=import-outside-toplevel,unused-import
