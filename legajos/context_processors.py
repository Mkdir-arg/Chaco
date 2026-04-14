from django.core.cache import cache
from django.utils.asyncio import async_unsafe

from .models import EventoCritico, AlertaEventoCritico

ALERTAS_CRITICAS_CACHE_TIMEOUT = 120


@async_unsafe
def alertas_eventos_criticos(request):
    """Context processor para mostrar alertas de eventos críticos al responsable"""

    if not request.user.is_authenticated:
        return {}

    cache_key = f'alertas_criticas_user_{request.user.id}'
    eventos_pendientes = cache.get(cache_key)
    if eventos_pendientes is None:
        try:
            eventos_pendientes = list(
                EventoCritico.objects.filter(
                    legajo__responsable=request.user
                ).exclude(
                    alertas_vistas__responsable=request.user
                ).select_related('legajo__ciudadano').order_by('-creado')[:5]
            )
            cache.set(cache_key, eventos_pendientes, ALERTAS_CRITICAS_CACHE_TIMEOUT)
        except Exception:
            eventos_pendientes = []

    return {'eventos_criticos_pendientes': eventos_pendientes}