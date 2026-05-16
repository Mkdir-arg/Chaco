from django.db.models import Q

from ..models import AlertaCiudadano, LegajoAtencion


class FiltrosUsuarioService:
    """Servicio para filtrar alertas según el usuario y sus permisos."""

    @staticmethod
    def obtener_alertas_usuario(usuario):
        if not usuario or not usuario.is_authenticated:
            return AlertaCiudadano.objects.none()

        if usuario.is_superuser:
            return AlertaCiudadano.objects.filter(activa=True)

        filtros = Q()

        legajos_responsable = LegajoAtencion.objects.filter(responsable=usuario).select_related(
            "dispositivo"
        )
        if legajos_responsable.exists():
            filtros |= Q(legajo__in=legajos_responsable)

        dispositivo_usuario = FiltrosUsuarioService._obtener_dispositivo_usuario(usuario)
        if dispositivo_usuario:
            legajos_dispositivo = LegajoAtencion.objects.filter(
                dispositivo=dispositivo_usuario
            ).select_related("dispositivo")
            filtros |= Q(legajo__in=legajos_dispositivo)

        grupos_usuario = usuario.groups.values_list("name", flat=True)

        if "Administrador" in grupos_usuario:
            return AlertaCiudadano.objects.filter(activa=True)

        if not filtros:
            filtros = Q(prioridad="CRITICA")

        return AlertaCiudadano.objects.filter(filtros, activa=True)

    @staticmethod
    def _obtener_dispositivo_usuario(usuario):
        legajo_responsable = LegajoAtencion.objects.filter(responsable=usuario).select_related(
            "dispositivo"
        ).first()
        if legajo_responsable:
            return legajo_responsable.dispositivo

        return None

    @staticmethod
    def puede_ver_alerta(usuario, alerta):
        if not usuario or not usuario.is_authenticated:
            return False

        if usuario.is_superuser:
            return True

        alertas_usuario = FiltrosUsuarioService.obtener_alertas_usuario(usuario)
        return alertas_usuario.filter(id=alerta.id).exists()

    @staticmethod
    def obtener_estadisticas_usuario(usuario):
        alertas_usuario = FiltrosUsuarioService.obtener_alertas_usuario(usuario)

        return {
            "total": alertas_usuario.count(),
            "criticas": alertas_usuario.filter(prioridad="CRITICA").count(),
            "altas": alertas_usuario.filter(prioridad="ALTA").count(),
            "medias": alertas_usuario.filter(prioridad="MEDIA").count(),
            "bajas": alertas_usuario.filter(prioridad="BAJA").count(),
        }
