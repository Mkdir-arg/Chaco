from django.db.models.signals import post_save
from django.dispatch import receiver

from ..models import LegajoAtencion
from ..models_programas import InscripcionPrograma, Programa


@receiver(post_save, sender=LegajoAtencion)
def crear_inscripcion_programa_sedronar(sender, instance, created, **kwargs):
    """Crea automáticamente una inscripción SEDRONAR al crear un legajo."""
    if created:
        try:
            programa_sedronar = Programa.objects.get(tipo="ACOMPANAMIENTO_SEDRONAR")

            existe = InscripcionPrograma.objects.filter(
                ciudadano=instance.ciudadano,
                programa=programa_sedronar,
            ).exists()

            if not existe:
                InscripcionPrograma.objects.create(
                    ciudadano=instance.ciudadano,
                    programa=programa_sedronar,
                    via_ingreso="DIRECTO",
                    estado="ACTIVO",
                    responsable=instance.responsable,
                    legajo_id=instance.id,
                    fecha_inscripcion=instance.fecha_apertura,
                    fecha_inicio=instance.fecha_apertura,
                    notas=f"Creado automáticamente desde LegajoAtencion {instance.codigo}",
                )
        except Programa.DoesNotExist:
            pass


@receiver(post_save, sender=InscripcionPrograma)
def iniciar_flujo_inscripcion(sender, instance, created, **kwargs):
    """Inicia el flujo del programa al crear una nueva inscripción, si el programa tiene flujo activo."""
    if created and instance.programa.flujo_activo:
        try:
            from flujos.runtime import FlowRuntime
            FlowRuntime.iniciar(instance)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(
                'No se pudo iniciar el flujo para inscripción %s: %s', instance.pk, exc
            )
