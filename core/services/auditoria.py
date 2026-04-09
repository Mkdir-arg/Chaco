from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone

from ..models_auditoria import AlertaAuditoria, LogAccion, LogDescargaArchivo, SesionUsuario


class ServicioAlertas:
    """Servicio para generar alertas automáticas de auditoría."""

    @staticmethod
    def verificar_multiples_logins():
        hace_1_hora = timezone.now() - timedelta(hours=1)

        usuarios_multiples_sesiones = (
            SesionUsuario.objects.filter(inicio_sesion__gte=hace_1_hora, activa=True)
            .select_related("usuario")
            .values("usuario")
            .annotate(sesiones_count=Count("id"))
            .filter(sesiones_count__gt=2)
        )

        for item in usuarios_multiples_sesiones:
            usuario = User.objects.get(id=item["usuario"])
            alerta_existente = AlertaAuditoria.objects.filter(
                tipo=AlertaAuditoria.TipoAlerta.MULTIPLES_LOGINS,
                usuario_afectado=usuario,
                timestamp__gte=hace_1_hora,
                revisada=False,
            ).exists()
            if not alerta_existente:
                AlertaAuditoria.objects.create(
                    tipo=AlertaAuditoria.TipoAlerta.MULTIPLES_LOGINS,
                    severidad=AlertaAuditoria.Severidad.MEDIA,
                    usuario_afectado=usuario,
                    descripcion=f"Usuario con {item['sesiones_count']} sesiones activas simultáneas",
                    detalles={"sesiones_count": item["sesiones_count"]},
                )

    @staticmethod
    def verificar_actividad_sospechosa():
        hace_10_minutos = timezone.now() - timedelta(minutes=10)

        usuarios_actividad_alta = (
            LogAccion.objects.filter(timestamp__gte=hace_10_minutos, usuario__isnull=False)
            .select_related("usuario")
            .values("usuario")
            .annotate(acciones_count=Count("id"))
            .filter(acciones_count__gt=50)
        )

        for item in usuarios_actividad_alta:
            usuario = User.objects.get(id=item["usuario"])
            hace_1_hora = timezone.now() - timedelta(hours=1)
            alerta_existente = AlertaAuditoria.objects.filter(
                tipo=AlertaAuditoria.TipoAlerta.ACTIVIDAD_SOSPECHOSA,
                usuario_afectado=usuario,
                timestamp__gte=hace_1_hora,
                revisada=False,
            ).exists()
            if not alerta_existente:
                AlertaAuditoria.objects.create(
                    tipo=AlertaAuditoria.TipoAlerta.ACTIVIDAD_SOSPECHOSA,
                    severidad=AlertaAuditoria.Severidad.ALTA,
                    usuario_afectado=usuario,
                    descripcion=f"Actividad inusualmente alta: {item['acciones_count']} acciones en 10 minutos",
                    detalles={"acciones_count": item["acciones_count"], "periodo": "10_minutos"},
                )

    @staticmethod
    def verificar_descarga_masiva():
        hace_1_hora = timezone.now() - timedelta(hours=1)

        usuarios_descargas_masivas = (
            LogDescargaArchivo.objects.filter(timestamp__gte=hace_1_hora, usuario__isnull=False)
            .select_related("usuario")
            .values("usuario")
            .annotate(descargas_count=Count("id"))
            .filter(descargas_count__gt=10)
        )

        for item in usuarios_descargas_masivas:
            usuario = User.objects.get(id=item["usuario"])
            alerta_existente = AlertaAuditoria.objects.filter(
                tipo=AlertaAuditoria.TipoAlerta.DESCARGA_MASIVA,
                usuario_afectado=usuario,
                timestamp__gte=hace_1_hora,
                revisada=False,
            ).exists()
            if not alerta_existente:
                AlertaAuditoria.objects.create(
                    tipo=AlertaAuditoria.TipoAlerta.DESCARGA_MASIVA,
                    severidad=AlertaAuditoria.Severidad.ALTA,
                    usuario_afectado=usuario,
                    descripcion=f"Descarga masiva detectada: {item['descargas_count']} archivos en 1 hora",
                    detalles={"descargas_count": item["descargas_count"], "periodo": "1_hora"},
                )

    @staticmethod
    def verificar_acceso_fuera_horario():
        ahora = timezone.now()
        hora_actual = ahora.hour

        if hora_actual < 7 or hora_actual > 22:
            hace_30_minutos = ahora - timedelta(minutes=30)
            logins_fuera_horario = LogAccion.objects.filter(
                accion=LogAccion.TipoAccion.LOGIN,
                timestamp__gte=hace_30_minutos,
                usuario__isnull=False,
            ).select_related("usuario")

            for login in logins_fuera_horario:
                hace_1_hora = ahora - timedelta(hours=1)
                alerta_existente = AlertaAuditoria.objects.filter(
                    tipo=AlertaAuditoria.TipoAlerta.ACCESO_FUERA_HORARIO,
                    usuario_afectado=login.usuario,
                    timestamp__gte=hace_1_hora,
                    revisada=False,
                ).exists()
                if not alerta_existente:
                    AlertaAuditoria.objects.create(
                        tipo=AlertaAuditoria.TipoAlerta.ACCESO_FUERA_HORARIO,
                        severidad=AlertaAuditoria.Severidad.MEDIA,
                        usuario_afectado=login.usuario,
                        descripcion=f"Acceso fuera del horario laboral a las {login.timestamp.strftime('%H:%M')}",
                        detalles={"hora_acceso": login.timestamp.strftime("%H:%M"), "ip": login.ip_address},
                    )

    @classmethod
    def ejecutar_verificaciones(cls):
        try:
            cls.verificar_multiples_logins()
            cls.verificar_actividad_sospechosa()
            cls.verificar_descarga_masiva()
            cls.verificar_acceso_fuera_horario()
        except Exception as exc:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error en verificaciones de auditoría: {exc}")


class ServicioReportes:
    """Servicio para generar reportes de auditoría."""

    @staticmethod
    def reporte_actividad_usuario(usuario, fecha_desde=None, fecha_hasta=None):
        if not fecha_desde:
            fecha_desde = timezone.now().date() - timedelta(days=30)
        if not fecha_hasta:
            fecha_hasta = timezone.now().date()

        acciones_stats = LogAccion.objects.filter(
            usuario=usuario,
            timestamp__date__range=[fecha_desde, fecha_hasta],
        ).aggregate(total_acciones=Count("id"), acciones_por_tipo=Count("accion"))

        descargas_count = LogDescargaArchivo.objects.filter(
            usuario=usuario,
            timestamp__date__range=[fecha_desde, fecha_hasta],
        ).count()

        sesiones = SesionUsuario.objects.filter(
            usuario=usuario,
            inicio_sesion__date__range=[fecha_desde, fecha_hasta],
        ).select_related("usuario")

        acciones_por_tipo = (
            LogAccion.objects.filter(
                usuario=usuario,
                timestamp__date__range=[fecha_desde, fecha_hasta],
            )
            .values("accion")
            .annotate(count=Count("id"))
        )

        return {
            "usuario": usuario,
            "periodo": {"desde": fecha_desde, "hasta": fecha_hasta},
            "total_acciones": acciones_stats["total_acciones"],
            "total_descargas": descargas_count,
            "total_sesiones": sesiones.count(),
            "acciones_por_tipo": acciones_por_tipo,
            "sesiones_promedio_duracion": ServicioReportes._calcular_duracion_promedio_sesiones(sesiones),
        }

    @staticmethod
    def _calcular_duracion_promedio_sesiones(sesiones):
        duraciones = []
        for sesion in sesiones:
            if sesion.fin_sesion:
                duraciones.append((sesion.fin_sesion - sesion.inicio_sesion).total_seconds())

        if duraciones:
            return timedelta(seconds=sum(duraciones) / len(duraciones))
        return timedelta(0)
