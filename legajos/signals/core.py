from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from core.cache_decorators import invalidate_cache_pattern

from ..models import Ciudadano, Derivacion, EventoCritico, LegajoAtencion, SeguimientoContacto


@receiver([post_save, post_delete], sender=Ciudadano)
def invalidate_ciudadano_cache(sender, **kwargs):
    """Invalida cache cuando se modifica un ciudadano."""
    from django.core.cache import cache

    cache.clear()


@receiver([post_save, post_delete], sender=LegajoAtencion)
def invalidate_legajo_cache(sender, **kwargs):
    """Invalida cache cuando se modifica un legajo."""
    invalidate_cache_pattern("legajos_list")
    invalidate_cache_pattern("reportes")
    invalidate_cache_pattern("dashboard")


@receiver([post_save, post_delete], sender=SeguimientoContacto)
def invalidate_seguimiento_cache(sender, **kwargs):
    """Invalida cache cuando se modifica un seguimiento."""
    invalidate_cache_pattern("seguimiento")
    invalidate_cache_pattern("reportes")


@receiver([post_save, post_delete], sender=Derivacion)
def invalidate_derivacion_cache(sender, **kwargs):
    """Invalida cache cuando se modifica una derivación."""
    invalidate_cache_pattern("derivacion")
    invalidate_cache_pattern("reportes")


@receiver([post_save, post_delete], sender=EventoCritico)
def invalidate_evento_cache(sender, **kwargs):
    """Invalida cache cuando se modifica un evento crítico."""
    invalidate_cache_pattern("evento")
    invalidate_cache_pattern("reportes")


