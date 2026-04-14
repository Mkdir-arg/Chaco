from django.core.cache import cache

from config.branding import get_branding_profile

from .models import DispositivoRed

DISPOSITIVOS_ACTIVOS_CACHE_KEY = 'dispositivos_activos_v1'
DISPOSITIVOS_ACTIVOS_CACHE_TIMEOUT = 1800


def dispositivos_context(request):
    """Agrega dispositivos al contexto global"""
    if request.user.is_authenticated and request.user.is_superuser:
        dispositivos = cache.get(DISPOSITIVOS_ACTIVOS_CACHE_KEY)
        if dispositivos is None:
            dispositivos = list(
                DispositivoRed.objects.filter(activo=True).order_by('nombre')
            )
            cache.set(
                DISPOSITIVOS_ACTIVOS_CACHE_KEY,
                dispositivos,
                DISPOSITIVOS_ACTIVOS_CACHE_TIMEOUT,
            )
        return {'todos_dispositivos': dispositivos}
    return {
        'todos_dispositivos': []
    }


def branding_context(request):
    """Expone el branding activo para templates globales."""
    return {
        "branding": get_branding_profile(),
    }
