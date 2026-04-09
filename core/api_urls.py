from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ProvinciaViewSet, MunicipioViewSet, LocalidadViewSet,
    InstitucionViewSet, DocumentoRequeridoViewSet, SexoViewSet, MesViewSet, DiaViewSet, TurnoViewSet
)

# Alias para compatibilidad
DispositivoRedViewSet = InstitucionViewSet

router = DefaultRouter()
router.register(r'provincias', ProvinciaViewSet)
router.register(r'municipios', MunicipioViewSet)
router.register(r'localidades', LocalidadViewSet)
router.register(r'instituciones', InstitucionViewSet)
router.register(r'documentos-requeridos', DocumentoRequeridoViewSet)
# Alias para compatibilidad hacia atrás
router.register(r'dispositivos', InstitucionViewSet, basename='dispositivo')
router.register(r'sexos', SexoViewSet)
router.register(r'meses', MesViewSet)
router.register(r'dias', DiaViewSet)
router.register(r'turnos', TurnoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]