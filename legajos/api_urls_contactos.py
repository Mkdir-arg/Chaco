from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views.contactos import (
    HistorialContactoViewSet, VinculoFamiliarViewSet, ProfesionalTratanteViewSet,
    DispositivoVinculadoViewSet, ContactoEmergenciaViewSet
)

router = DefaultRouter()
router.register(r'historial-contactos', HistorialContactoViewSet)
router.register(r'vinculos-familiares', VinculoFamiliarViewSet)
router.register(r'profesionales-tratantes', ProfesionalTratanteViewSet)
router.register(r'dispositivos-vinculados', DispositivoVinculadoViewSet)
router.register(r'contactos-emergencia', ContactoEmergenciaViewSet)

urlpatterns = [
    path('contactos/', include(router.urls)),
]
