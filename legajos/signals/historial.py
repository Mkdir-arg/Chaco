from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from ..models import (
    Derivacion,
    HistorialActividad,
    HistorialDerivacion,
    HistorialInscripto,
    HistorialStaff,
    InscriptoActividad,
    PlanFortalecimiento,
    StaffActividad,
)


@receiver(post_save, sender=PlanFortalecimiento)
def crear_historial_actividad(sender, instance, created, **kwargs):
    if created:
        HistorialActividad.objects.create(
            actividad=instance,
            accion="CREACION",
            descripcion=f'Actividad "{instance.nombre}" creada',
        )


@receiver(pre_save, sender=PlanFortalecimiento)
def guardar_estado_anterior_actividad(sender, instance, **kwargs):
    if instance.pk:
        try:
            anterior = PlanFortalecimiento.objects.get(pk=instance.pk)
            if anterior.estado != instance.estado:
                accion_map = {
                    "SUSPENDIDO": "SUSPENSION",
                    "FINALIZADO": "FINALIZACION",
                    "ACTIVO": "REACTIVACION",
                }
                accion = accion_map.get(instance.estado, "MODIFICACION")
                HistorialActividad.objects.create(
                    actividad=instance,
                    accion=accion,
                    descripcion=(
                        f"Estado cambiado de {anterior.get_estado_display()} "
                        f"a {instance.get_estado_display()}"
                    ),
                )
        except PlanFortalecimiento.DoesNotExist:
            pass


@receiver(post_save, sender=StaffActividad)
def crear_historial_staff(sender, instance, created, **kwargs):
    if created:
        nombre_completo = f"{instance.personal.nombre} {instance.personal.apellido}"
        HistorialStaff.objects.create(
            staff=instance,
            accion="ASIGNACION",
            descripcion=f"{nombre_completo} asignado como {instance.rol_en_actividad}",
        )


@receiver(pre_save, sender=Derivacion)
def guardar_estado_anterior_derivacion(sender, instance, **kwargs):
    if instance.pk:
        try:
            anterior = Derivacion.objects.get(pk=instance.pk)
            if anterior.estado != instance.estado:
                accion_map = {"ACEPTADA": "ACEPTACION", "RECHAZADA": "RECHAZO"}
                accion = accion_map.get(instance.estado, "CREACION")
                HistorialDerivacion.objects.create(
                    derivacion=instance,
                    accion=accion,
                    descripcion=f"Derivación {accion.lower()}",
                    estado_anterior=anterior.estado,
                )
        except Derivacion.DoesNotExist:
            pass


@receiver(post_save, sender=InscriptoActividad)
def crear_historial_inscripto(sender, instance, created, **kwargs):
    if created:
        HistorialInscripto.objects.create(
            inscripto=instance,
            accion="INSCRIPCION",
            descripcion=f"{instance.ciudadano.nombre_completo} inscrito en {instance.actividad.nombre}",
        )


@receiver(pre_save, sender=InscriptoActividad)
def guardar_estado_anterior_inscripto(sender, instance, **kwargs):
    if instance.pk:
        try:
            anterior = InscriptoActividad.objects.get(pk=instance.pk)
            if anterior.estado != instance.estado:
                accion_map = {
                    "ACTIVO": "ACTIVACION",
                    "FINALIZADO": "FINALIZACION",
                    "ABANDONADO": "ABANDONO",
                }
                accion = accion_map.get(instance.estado, "INSCRIPCION")
                HistorialInscripto.objects.create(
                    inscripto=instance,
                    accion=accion,
                    descripcion=f"Estado cambiado a {instance.get_estado_display()}",
                    estado_anterior=anterior.estado,
                )
        except InscriptoActividad.DoesNotExist:
            pass
