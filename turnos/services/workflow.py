from django.db import transaction
from django.utils import timezone

from portal.models import TurnoCiudadano

from .notifications import enviar_email_cancelacion, enviar_email_confirmacion


class TurnoActionError(Exception):
    pass


class TurnosBackofficeService:
    @staticmethod
    def actualizar_notas(turno, notas):
        turno.notas_backoffice = notas.strip()
        turno.save(update_fields=["notas_backoffice", "modificado"])
        return turno

    @staticmethod
    @transaction.atomic
    def aprobar_turno(turno_id, user, notas=""):
        turno = TurnoCiudadano.objects.select_for_update().get(pk=turno_id)
        if turno.estado != TurnoCiudadano.Estado.PENDIENTE:
            raise TurnoActionError("Este turno ya fue procesado por otro operador.")

        if notas:
            turno.notas_backoffice = notas
        turno.estado = TurnoCiudadano.Estado.CONFIRMADO
        turno.aprobado_por = user
        turno.fecha_aprobacion = timezone.now()
        turno.save()
        transaction.on_commit(lambda: enviar_email_confirmacion(turno))
        return turno

    @staticmethod
    @transaction.atomic
    def rechazar_turno(turno_id, user, motivo):
        turno = TurnoCiudadano.objects.select_for_update().get(pk=turno_id)
        if turno.estado != TurnoCiudadano.Estado.PENDIENTE:
            raise TurnoActionError("Este turno ya fue procesado por otro operador.")

        turno.estado = TurnoCiudadano.Estado.CANCELADO_SISTEMA
        turno.notas_backoffice = motivo
        turno.aprobado_por = user
        turno.fecha_aprobacion = timezone.now()
        turno.save()
        transaction.on_commit(
            lambda: enviar_email_cancelacion(turno, motivo=motivo)
        )
        return turno

    @staticmethod
    def cancelar_turno(turno, motivo):
        if turno.estado not in [
            TurnoCiudadano.Estado.PENDIENTE,
            TurnoCiudadano.Estado.CONFIRMADO,
        ]:
            raise TurnoActionError("Este turno no puede cancelarse.")

        turno.estado = TurnoCiudadano.Estado.CANCELADO_SISTEMA
        turno.notas_backoffice = motivo
        turno.save()
        enviar_email_cancelacion(turno, motivo=motivo)
        return turno

    @staticmethod
    def completar_turno(turno):
        if turno.estado != TurnoCiudadano.Estado.CONFIRMADO:
            raise TurnoActionError("Solo pueden completarse turnos confirmados.")

        turno.estado = TurnoCiudadano.Estado.COMPLETADO
        turno.save(update_fields=["estado", "modificado"])
        return turno
