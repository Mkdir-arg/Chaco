"""Reglas derivadas de ocupación para camas de Dispositivos."""

from django.core.exceptions import ValidationError
from django.db import transaction

from programas.models import Admision, Cama


def resumen_ocupacion(dispositivo):
    """Devuelve la ocupación real, calculada desde camas y estadías alojadas."""

    camas = Cama.objects.filter(dispositivo=dispositivo)
    totales = camas.count()
    fuera_servicio = camas.filter(estado=Cama.Estado.FUERA_SERVICIO).count()
    operativas = max(totales - fuera_servicio, 0)
    ocupadas = (
        Admision.objects.filter(
            dispositivo=dispositivo,
            estado=Admision.Estado.ALOJADO,
            cama__isnull=False,
        )
        .values("cama_id")
        .distinct()
        .count()
    )
    libres = max(operativas - ocupadas, 0)
    porcentaje = round((ocupadas * 100) / operativas) if operativas else 0
    umbral_amarillo = getattr(dispositivo.tipo, "umbral_ocupacion_amarillo", 50)
    umbral_rojo = getattr(dispositivo.tipo, "umbral_ocupacion_rojo", 80)
    semaforo = "ROJO" if porcentaje >= umbral_rojo else "AMARILLO" if porcentaje >= umbral_amarillo else "VERDE"

    return {
        "totales": totales,
        "ocupadas": ocupadas,
        "fuera_servicio": fuera_servicio,
        "operativas": operativas,
        "libres": libres,
        "porcentaje": porcentaje,
        "semaforo": semaforo,
    }


def cambiar_estado_cama(cama, nuevo_estado):
    """Cambia el estado de una cama sin perder la seguridad de una estadía activa."""

    with transaction.atomic():
        cama = Cama.objects.select_for_update().get(pk=cama.pk)
        tiene_persona_alojada = Admision.objects.filter(
            cama=cama,
            estado=Admision.Estado.ALOJADO,
        ).exists()
        if tiene_persona_alojada and nuevo_estado != Cama.Estado.OCUPADA:
            raise ValidationError("La cama tiene una persona alojada: exige reasignación previa.")
        if nuevo_estado == Cama.Estado.OCUPADA and not tiene_persona_alojada:
            raise ValidationError("La ocupación se deriva de una estadía activa, no se carga manualmente.")
        cama.estado = nuevo_estado
        cama.save(update_fields=["estado", "modificado"])
        return cama


def crear_camas(dispositivo, cantidad):
    """Agrega camas disponibles con código consecutivo y sincroniza la capacidad."""

    if cantidad <= 0:
        raise ValidationError("Indicá una cantidad positiva de camas.")

    with transaction.atomic():
        dispositivo = dispositivo.__class__.objects.select_for_update().get(pk=dispositivo.pk)
        if not dispositivo.tipo.maneja_camas:
            raise ValidationError("El tipo de dispositivo no maneja camas.")

        codigos_existentes = set(Cama.objects.filter(dispositivo=dispositivo).values_list("codigo", flat=True))
        creadas = []
        numero = 1
        while len(creadas) < cantidad:
            codigo = f"C-{numero:02d}"
            if codigo not in codigos_existentes:
                creadas.append(Cama.objects.create(dispositivo=dispositivo, codigo=codigo))
                codigos_existentes.add(codigo)
            numero += 1

        dispositivo.camas_totales = len(codigos_existentes)
        dispositivo.save(update_fields=["camas_totales", "modificado"])
        return creadas
