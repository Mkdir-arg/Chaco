from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    CiudadanoViewSet, LegajoAtencionViewSet, EvaluacionInicialViewSet,
    PlanIntervencionViewSet, SeguimientoContactoViewSet, 
    DerivacionViewSet, EventoCriticoViewSet, AlertasViewSet
)

router = DefaultRouter()
router.register(r'ciudadanos', CiudadanoViewSet)
router.register(r'legajos', LegajoAtencionViewSet)
router.register(r'evaluaciones', EvaluacionInicialViewSet)
router.register(r'planes', PlanIntervencionViewSet)
router.register(r'seguimientos', SeguimientoContactoViewSet)
router.register(r'derivaciones', DerivacionViewSet)
router.register(r'eventos', EventoCriticoViewSet)
router.register(r'alertas', AlertasViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('legajos.api_urls_contactos')),
]
