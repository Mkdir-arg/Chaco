from datetime import datetime, timedelta

from django.db.models import Count, Q
from django.utils import timezone
from django.utils.html import escape
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from legajos.models import AlertaCiudadano, Ciudadano, LegajoAtencion, SeguimientoContacto
from users.models import User

import logging

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def metricas_dashboard(request):
    """Obtiene metricas principales del dashboard."""
    total_ciudadanos = Ciudadano.objects.count()
    legajos_activos = LegajoAtencion.objects.filter(estado__in=["ABIERTO", "EN_SEGUIMIENTO"]).count()
    alertas_activas = AlertaCiudadano.objects.filter(activa=True).count()

    hoy = timezone.now().date()
    seguimientos_hoy = SeguimientoContacto.objects.filter(creado__date=hoy).count()

    estados = LegajoAtencion.objects.values("estado").annotate(count=Count("id"))
    estados_dict = {estado["estado"]: estado["count"] for estado in estados}

    hace_24h = timezone.now() - timedelta(hours=24)
    usuarios_activos = User.objects.filter(last_login__gte=hace_24h).count()

    return Response(
        {
            "metricas": {
                "ciudadanos": total_ciudadanos,
                "legajos": legajos_activos,
                "seguimientos": seguimientos_hoy,
                "alertas": alertas_activas,
            },
            "estados_legajos": {
                "abiertos": estados_dict.get("ABIERTO", 0),
                "seguimiento": estados_dict.get("EN_SEGUIMIENTO", 0),
                "derivados": estados_dict.get("DERIVADO", 0),
                "cerrados": estados_dict.get("CERRADO", 0),
            },
            "usuarios_conectados": usuarios_activos,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def buscar_ciudadanos(request):
    """Busqueda rapida de ciudadanos."""
    query = escape(request.GET.get("q", "").strip())

    if len(query) < 3:
        return Response({"results": []})

    try:
        ciudadanos = (
            Ciudadano.objects.only("id", "nombre", "apellido", "dni")
            .filter(Q(nombre__icontains=query) | Q(apellido__icontains=query) | Q(dni__icontains=query))[:8]
        )

        resultados = [{"id": c.id, "nombre": f"{c.apellido}, {c.nombre}", "dni": c.dni} for c in ciudadanos]
        return Response({"results": resultados})
    except Exception as e:
        logger.error(f"Error en busqueda de ciudadanos: {e}", exc_info=True)
        return Response({"results": [], "error": "Error en la busqueda"}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def alertas_criticas(request):
    """Obtiene alertas criticas activas."""
    try:
        alertas = (
            AlertaCiudadano.objects.filter(activa=True, prioridad__in=["CRITICA", "ALTA"])
            .select_related("ciudadano")
            .order_by("-creado")[:5]
        )

        alertas_data = []
        for alerta in alertas:
            ciudadano_nombre = "Sin ciudadano"
            if getattr(alerta, "ciudadano", None):
                apellido = alerta.ciudadano.apellido or ""
                nombre = alerta.ciudadano.nombre or ""
                ciudadano_nombre = f"{apellido}, {nombre}".strip(", ").strip() or "Sin ciudadano"

            alertas_data.append(
                {
                    "id": alerta.id,
                    "ciudadano": ciudadano_nombre,
                    "tipo": alerta.get_tipo_display(),
                    "prioridad": alerta.prioridad,
                    "fecha": alerta.creado.strftime("%d/%m %H:%M"),
                    "mensaje": alerta.mensaje,
                }
            )

        return Response({"results": alertas_data})
    except Exception as e:
        logger.error(f"Error en alertas_criticas: {e}", exc_info=True)
        return Response({"results": []}, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def actividad_reciente(request):
    """Obtiene actividad reciente del sistema."""
    try:
        legajos_nuevos = LegajoAtencion.objects.select_related("ciudadano", "responsable").order_by("-creado")[:3]
        seguimientos = (
            SeguimientoContacto.objects.select_related("legajo__ciudadano", "profesional__usuario").order_by("-creado")[:3]
        )
        alertas = AlertaCiudadano.objects.select_related("ciudadano").filter(activa=True).order_by("-creado")[:2]

        actividades = []

        for legajo in legajos_nuevos:
            apellido = getattr(legajo.ciudadano, "apellido", "") or ""
            nombre = getattr(legajo.ciudadano, "nombre", "") or ""
            ciudadano_nombre = f"{apellido}, {nombre}".strip(", ").strip() or "Ciudadano"
            usuario = legajo.responsable.get_full_name() if legajo.responsable else "Sistema"

            actividades.append(
                {
                    "descripcion": f"Nuevo legajo para {ciudadano_nombre}",
                    "usuario": usuario,
                    "tiempo": _tiempo_relativo(legajo.creado),
                    "timestamp": legajo.creado.isoformat(),
                    "tipo": "create",
                    "icono": "fas fa-plus",
                }
            )

        for seguimiento in seguimientos:
            usuario = "Sistema"
            if seguimiento.profesional and seguimiento.profesional.usuario:
                usuario = seguimiento.profesional.usuario.get_full_name() or seguimiento.profesional.usuario.username

            actividades.append(
                {
                    "descripcion": f"Seguimiento: {seguimiento.get_tipo_display()}",
                    "usuario": usuario,
                    "tiempo": _tiempo_relativo(seguimiento.creado),
                    "timestamp": seguimiento.creado.isoformat(),
                    "tipo": "update",
                    "icono": "fas fa-check",
                }
            )

        for alerta in alertas:
            actividades.append(
                {
                    "descripcion": f"Alerta: {alerta.get_tipo_display()}",
                    "usuario": "Sistema",
                    "tiempo": _tiempo_relativo(alerta.creado),
                    "timestamp": alerta.creado.isoformat(),
                    "tipo": "alert",
                    "icono": "fas fa-exclamation-triangle",
                }
            )

        actividades.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        for item in actividades:
            item.pop("timestamp", None)

        return Response({"results": actividades[:8]})
    except Exception as e:
        logger.error(f"Error en actividad_reciente: {e}", exc_info=True)
        return Response({"results": []}, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def tendencias_datos(request):
    """Obtiene datos para grafico de tendencias."""
    periodo = request.GET.get("periodo", "30d")
    dias_map = {"7d": 7, "30d": 30, "90d": 90}
    dias = dias_map.get(periodo, 30)

    try:
        fecha_inicio = timezone.now().date() - timedelta(days=dias)

        from django.db.models.functions import TruncDate

        legajos_por_fecha = (
            LegajoAtencion.objects.filter(fecha_apertura__gte=fecha_inicio)
            .annotate(fecha=TruncDate("fecha_apertura"))
            .values("fecha")
            .annotate(count=Count("id"))
            .order_by("fecha")
        )

        datos_dict = {item["fecha"]: item["count"] for item in legajos_por_fecha}

        datos = []
        labels = []
        for i in range(dias):
            fecha = fecha_inicio + timedelta(days=i)
            datos.append(datos_dict.get(fecha, 0))
            labels.append(fecha.strftime("%d/%m"))

        return Response({"labels": labels, "datos": datos})
    except Exception as e:
        logger.error(f"Error en tendencias: {e}", exc_info=True)
        return Response({"labels": [], "datos": []}, status=500)


def _tiempo_relativo(fecha):
    """Convierte fecha a tiempo relativo."""
    if isinstance(fecha, datetime):
        fecha = fecha.replace(tzinfo=None)
    elif hasattr(fecha, "date"):
        fecha = datetime.combine(fecha, datetime.min.time())

    ahora = datetime.now()
    diff = ahora - fecha

    if diff.days > 0:
        return f"Hace {diff.days} dia{'s' if diff.days > 1 else ''}"
    if diff.seconds > 3600:
        horas = diff.seconds // 3600
        return f"Hace {horas} hora{'s' if horas > 1 else ''}"
    if diff.seconds > 60:
        minutos = diff.seconds // 60
        return f"Hace {minutos} minuto{'s' if minutos > 1 else ''}"
    return "Hace unos segundos"
