import logging

from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def enviar_email_confirmacion(turno):
    """Envía email de confirmación al ciudadano. Best-effort: nunca bloquea el flujo."""
    ciudadano = turno.ciudadano
    email = getattr(ciudadano, 'email', '') or ''

    if not email:
        logger.warning(
            'Turno %s: ciudadano %s sin email — notificación de confirmación no enviada.',
            turno.codigo_turno, ciudadano,
        )
        return

    nombre_entidad = turno.nombre_entidad
    try:
        cuerpo = render_to_string('turnos/emails/turno_confirmado.html', {
            'turno': turno,
            'ciudadano': ciudadano,
            'nombre_entidad': nombre_entidad,
        })
        send_mail(
            subject=f'Turno confirmado — {nombre_entidad}',
            message=f'Tu turno {turno.codigo_turno} del {turno.fecha.strftime("%d/%m/%Y")} a las {turno.hora_inicio.strftime("%H:%M")} fue confirmado.',
            from_email=None,
            recipient_list=[email],
            html_message=cuerpo,
            fail_silently=False,
        )
        turno.email_confirmacion_enviado = True
        turno.save(update_fields=['email_confirmacion_enviado'])
        logger.info('Email de confirmación enviado para turno %s a %s.', turno.codigo_turno, email)
    except Exception as exc:
        logger.error(
            'Error enviando email de confirmación para turno %s: %s', turno.codigo_turno, exc
        )


def enviar_email_cancelacion(turno, motivo=''):
    """Envía email de cancelación al ciudadano. Best-effort: nunca bloquea el flujo."""
    ciudadano = turno.ciudadano
    email = getattr(ciudadano, 'email', '') or ''

    if not email:
        logger.warning(
            'Turno %s: ciudadano %s sin email — notificación de cancelación no enviada.',
            turno.codigo_turno, ciudadano,
        )
        return

    nombre_entidad = turno.nombre_entidad
    try:
        cuerpo = render_to_string('turnos/emails/turno_cancelado.html', {
            'turno': turno,
            'ciudadano': ciudadano,
            'nombre_entidad': nombre_entidad,
            'motivo': motivo,
        })
        send_mail(
            subject=f'Turno cancelado — {nombre_entidad}',
            message=f'Tu turno {turno.codigo_turno} del {turno.fecha.strftime("%d/%m/%Y")} fue cancelado. Motivo: {motivo}',
            from_email=None,
            recipient_list=[email],
            html_message=cuerpo,
            fail_silently=False,
        )
        turno.email_cancelacion_enviado = True
        turno.save(update_fields=['email_cancelacion_enviado'])
        logger.info('Email de cancelación enviado para turno %s a %s.', turno.codigo_turno, email)
    except Exception as exc:
        logger.error(
            'Error enviando email de cancelación para turno %s: %s', turno.codigo_turno, exc
        )
