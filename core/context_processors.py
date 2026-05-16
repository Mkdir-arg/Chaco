from django.core.cache import cache

from config.branding import get_branding_profile

def branding_context(request):
    """Expone el branding activo para templates globales."""
    return {
        "branding": get_branding_profile(),
    }
