from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from ..models import (
    AlertaCiudadano,
    Ciudadano,
    Consentimiento,
    Derivacion,
    EvaluacionInicial,
    EventoCritico,
    LegajoAtencion,
    PlanIntervencion,
)
from ..models_contactos import HistorialContacto, VinculoFamiliar


class AlertasService:
    """Servicio para generar y gestionar alertas automáticas."""

    @staticmethod
    def generar_alertas_ciudadano(ciudadano_id):
        """Genera todas las alertas para un ciudadano específico."""
        try:
            ciudadano = Ciudadano.objects.get(id=ciudadano_id)
            legajos = LegajoAtencion.objects.filter(ciudadano=ciudadano).select_related(
                "ciudadano",
                "dispositivo",
                "responsable",
            ).prefetch_related("evaluacion", "seguimientos", "eventos", "derivaciones")

            AlertaCiudadano.objects.filter(
                ciudadano=ciudadano,
                activa=True,
                prioridad__in=["MEDIA", "BAJA"],
            ).update(activa=False)

            alertas_generadas = []

            for legajo in legajos:
                alertas_generadas.extend(AlertasService._generar_alertas_legajo(legajo))

            alertas_generadas.extend(AlertasService._generar_alertas_generales(ciudadano))

            return alertas_generadas

        except Exception as exc:
            print(f"Error generando alertas: {exc}")
            return []

    @staticmethod
    def _generar_alertas_legajo(legajo):
        """Genera alertas específicas de un legajo."""
        alertas = []

        if legajo.nivel_riesgo == "ALTO":
            alertas.append(
                AlertasService._crear_alerta(
                    legajo.ciudadano,
                    legajo,
                    "RIESGO_ALTO",
                    "ALTA",
                    "Legajo con nivel de riesgo alto",
                )
            )

        if not hasattr(legajo, "evaluacion"):
            dias_sin_eval = (timezone.now().date() - legajo.fecha_apertura).days
            if dias_sin_eval > 15:
                alertas.append(
                    AlertasService._crear_alerta(
                        legajo.ciudadano,
                        legajo,
                        "SIN_EVALUACION",
                        "MEDIA",
                        f"Sin evaluación inicial hace {dias_sin_eval} días",
                    )
                )

        try:
            evaluacion = legajo.evaluacion
            if evaluacion.riesgo_suicida:
                alertas.append(
                    AlertasService._crear_alerta(
                        legajo.ciudadano,
                        legajo,
                        "RIESGO_SUICIDA",
                        "CRITICA",
                        "Riesgo suicida identificado en evaluación",
                    )
                )
            if evaluacion.violencia:
                alertas.append(
                    AlertasService._crear_alerta(
                        legajo.ciudadano,
                        legajo,
                        "VIOLENCIA",
                        "CRITICA",
                        "Situación de violencia identificada",
                    )
                )
        except Exception:
            pass

        if legajo.estado in ["ABIERTO", "EN_SEGUIMIENTO"] and not legajo.plan_vigente:
            alertas.append(
                AlertasService._crear_alerta(
                    legajo.ciudadano,
                    legajo,
                    "SIN_PLAN",
                    "MEDIA",
                    "Legajo activo sin plan de intervención",
                )
            )

        ultimo_contacto = HistorialContacto.objects.filter(legajo=legajo).select_related(
            "legajo__ciudadano"
        ).order_by("-fecha_contacto").first()

        if ultimo_contacto:
            dias_sin_contacto = (
                timezone.now().date() - ultimo_contacto.fecha_contacto.date()
            ).days
            if dias_sin_contacto > 30:
                alertas.append(
                    AlertasService._crear_alerta(
                        legajo.ciudadano,
                        legajo,
                        "SIN_CONTACTO",
                        "ALTA",
                        f"Sin contacto hace {dias_sin_contacto} días",
                    )
                )

        contactos_fallidos = HistorialContacto.objects.filter(
            legajo=legajo,
            estado="NO_CONTESTA",
            fecha_contacto__gte=timezone.now() - timedelta(days=30),
        ).count()

        if contactos_fallidos >= 3:
            alertas.append(
                AlertasService._crear_alerta(
                    legajo.ciudadano,
                    legajo,
                    "CONTACTOS_FALLIDOS",
                    "MEDIA",
                    f"{contactos_fallidos} contactos fallidos en el último mes",
                )
            )

        eventos_recientes = EventoCritico.objects.filter(
            legajo=legajo,
            creado__gte=timezone.now() - timedelta(days=7),
        ).count()

        if eventos_recientes > 0:
            alertas.append(
                AlertasService._crear_alerta(
                    legajo.ciudadano,
                    legajo,
                    "EVENTO_CRITICO",
                    "CRITICA",
                    f"{eventos_recientes} evento(s) crítico(s) en la última semana",
                )
            )

        derivaciones_pendientes = Derivacion.objects.filter(
            legajo=legajo,
            estado="PENDIENTE",
            creado__lte=timezone.now() - timedelta(days=7),
        ).count()

        if derivaciones_pendientes > 0:
            alertas.append(
                AlertasService._crear_alerta(
                    legajo.ciudadano,
                    legajo,
                    "DERIVACION_PENDIENTE",
                    "MEDIA",
                    f"{derivaciones_pendientes} derivación(es) pendiente(s)",
                )
            )

        try:
            from ..models import SeguimientoContacto

            seguimientos_vencidos = SeguimientoContacto.objects.filter(
                legajo=legajo,
                fecha_proximo_contacto__lt=timezone.now().date(),
                fecha_proximo_contacto__isnull=False,
            ).count()

            if seguimientos_vencidos > 0:
                alertas.append(
                    AlertasService._crear_alerta(
                        legajo.ciudadano,
                        legajo,
                        "SEGUIMIENTO_VENCIDO",
                        "ALTA",
                        f"{seguimientos_vencidos} seguimiento(s) vencido(s)",
                    )
                )
        except Exception:
            pass

        try:
            seguimientos_recientes = SeguimientoContacto.objects.filter(
                legajo=legajo,
                creado__gte=timezone.now() - timedelta(days=30),
                adherencia__in=["BAJA", "NULA"],
            ).count()

            if seguimientos_recientes >= 2:
                alertas.append(
                    AlertasService._crear_alerta(
                        legajo.ciudadano,
                        legajo,
                        "ADHERENCIA_BAJA",
                        "ALTA",
                        f"Adherencia baja en {seguimientos_recientes} seguimientos recientes",
                    )
                )
        except Exception:
            pass

        return alertas

    @staticmethod
    def _generar_alertas_generales(ciudadano):
        """Genera alertas generales del ciudadano."""
        alertas = []

        vinculos = VinculoFamiliar.objects.filter(
            ciudadano_principal=ciudadano,
            activo=True,
        ).count()

        if vinculos == 0:
            alertas.append(
                AlertasService._crear_alerta(
                    ciudadano,
                    None,
                    "SIN_RED_FAMILIAR",
                    "BAJA",
                    "Sin vínculos familiares registrados",
                )
            )

        consentimiento_vigente = Consentimiento.objects.filter(
            ciudadano=ciudadano,
            vigente=True,
        ).exists()

        if not consentimiento_vigente:
            alertas.append(
                AlertasService._crear_alerta(
                    ciudadano,
                    None,
                    "SIN_CONSENTIMIENTO",
                    "MEDIA",
                    "Sin consentimiento informado vigente",
                )
            )

        return alertas

    @staticmethod
    def _crear_alerta(ciudadano, legajo, tipo, prioridad, mensaje):
        """Crea una alerta si no existe una similar activa."""
        alerta_existente = AlertaCiudadano.objects.filter(
            ciudadano=ciudadano,
            legajo=legajo,
            tipo=tipo,
            activa=True,
        ).first()

        if not alerta_existente:
            alerta = AlertaCiudadano.objects.create(
                ciudadano=ciudadano,
                legajo=legajo,
                tipo=tipo,
                prioridad=prioridad,
                mensaje=mensaje,
            )
            AlertasService._enviar_notificacion_alerta(alerta)
            return alerta

        return alerta_existente

    @staticmethod
    def _enviar_notificacion_alerta(alerta):
        """Envía notificación WebSocket para nueva alerta."""
        try:
            channel_layer = get_channel_layer()

            alerta_data = {
                "id": alerta.id,
                "ciudadano": alerta.ciudadano.nombre_completo,
                "ciudadano_id": alerta.ciudadano.id,
                "tipo": alerta.tipo,
                "prioridad": alerta.prioridad,
                "mensaje": alerta.mensaje,
                "fecha": alerta.creado.strftime("%d/%m/%Y %H:%M"),
                "legajo_id": alerta.legajo.id if alerta.legajo else None,
            }

            async_to_sync(channel_layer.group_send)(
                "alertas_sistema",
                {"type": "nueva_alerta", "alerta": alerta_data},
            )

            if alerta.prioridad == "CRITICA":
                async_to_sync(channel_layer.group_send)(
                    "alertas_criticas",
                    {"type": "nueva_alerta_critica", "alerta": alerta_data},
                )
        except Exception as exc:
            print(f"Error enviando notificación WebSocket: {exc}")

    @staticmethod
    def obtener_alertas_ciudadano(ciudadano_id):
        """Obtiene alertas activas de un ciudadano."""
        return AlertaCiudadano.objects.filter(
            ciudadano_id=ciudadano_id,
            activa=True,
        ).select_related("legajo").order_by("-prioridad", "-creado")

    @staticmethod
    def cerrar_alerta(alerta_id, usuario=None):
        """Cierra una alerta específica."""
        try:
            alerta = AlertaCiudadano.objects.get(id=alerta_id)
            alerta.activa = False
            alerta.fecha_cierre = timezone.now()
            if usuario:
                alerta.cerrada_por = usuario
            alerta.save()
            return True
        except AlertaCiudadano.DoesNotExist:
            return False

    @staticmethod
    def generar_alerta_mensaje_ciudadano(conversacion):
        """Genera alerta cuando un ciudadano envía un mensaje."""
        if not conversacion or not hasattr(conversacion, "ciudadano"):
            return None

        return AlertasService._crear_alerta(
            conversacion.ciudadano,
            None,
            "MENSAJE_CIUDADANO",
            "MEDIA",
            "Nuevo mensaje del ciudadano en conversación",
        )

    @staticmethod
    def generar_alerta_seguimiento_vencido(seguimiento):
        """Genera alerta por seguimiento vencido."""
        if not seguimiento or not seguimiento.legajo:
            return None

        return AlertasService._crear_alerta(
            seguimiento.legajo.ciudadano,
            seguimiento.legajo,
            "SEGUIMIENTO_VENCIDO",
            "ALTA",
            "Seguimiento con fecha vencida",
        )

    @staticmethod
    def generar_alerta_evento_critico(legajo, tipo_evento, descripcion):
        """Genera alerta por evento crítico."""
        if not legajo:
            return None

        return AlertasService._crear_alerta(
            legajo.ciudadano,
            legajo,
            tipo_evento,
            "CRITICA",
            descripcion,
        )
