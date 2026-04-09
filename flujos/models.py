"""
Motor de Flujos — Modelos de configuración y ejecución (US-006).
"""
import logging

from django.conf import settings
from django.db import models, transaction

from core.models import TimeStamped

logger = logging.getLogger(__name__)


class Flujo(TimeStamped):
    """
    Configuración de flujo asociada a un programa.
    Un programa tiene como máximo un flujo definido.
    """

    programa = models.OneToOneField(
        'legajos.Programa',
        on_delete=models.PROTECT,
        related_name='flujo',
        verbose_name='Programa',
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre',
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción',
    )

    class Meta:
        verbose_name = 'Flujo'
        verbose_name_plural = 'Flujos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.programa.nombre})'


class VersionFlujo(models.Model):
    """
    Versión versionada de la definición JSON de un flujo.
    El número de versión es auto-incremental por flujo.
    Solo una versión puede estar en estado PUBLICADA por flujo.
    """

    class Estado(models.TextChoices):
        BORRADOR = 'BORRADOR', 'Borrador'
        PUBLICADA = 'PUBLICADA', 'Publicada'
        ARCHIVADA = 'ARCHIVADA', 'Archivada'

    flujo = models.ForeignKey(
        Flujo,
        on_delete=models.CASCADE,
        related_name='versiones',
        verbose_name='Flujo',
    )
    numero_version = models.PositiveIntegerField(
        verbose_name='Número de versión',
        db_index=True,
    )
    definicion = models.JSONField(
        verbose_name='Definición',
        help_text='JSON con nodos y transiciones del flujo',
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.BORRADOR,
        db_index=True,
        verbose_name='Estado',
    )
    fecha_publicacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de publicación',
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='versiones_flujo_creadas',
        verbose_name='Creado por',
    )

    class Meta:
        verbose_name = 'Versión de flujo'
        verbose_name_plural = 'Versiones de flujo'
        ordering = ['flujo', '-numero_version']
        constraints = [
            models.UniqueConstraint(
                fields=['flujo', 'numero_version'],
                name='uq_versionflujo_flujo_numero',
            ),
        ]
        indexes = [
            models.Index(fields=['flujo', 'estado'], name='ix_versionflujo_flujo_estado'),
        ]

    def __str__(self):
        return f'{self.flujo.nombre} v{self.numero_version} ({self.estado})'

    def save(self, *args, **kwargs):
        if self._state.adding and not self.numero_version:
            with transaction.atomic():
                from django.db.models import Max
                ultimo = (
                    VersionFlujo.objects
                    .filter(flujo=self.flujo)
                    .select_for_update()
                    .aggregate(max_v=Max('numero_version'))
                )['max_v'] or 0
                self.numero_version = ultimo + 1
        super().save(*args, **kwargs)


class InstanciaFlujo(models.Model):
    """
    Ejecución activa de un flujo para una inscripción específica.
    Una inscripción tiene como máximo una instancia de flujo.
    """

    class Estado(models.TextChoices):
        ACTIVA = 'ACTIVA', 'Activa'
        COMPLETADA = 'COMPLETADA', 'Completada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    inscripcion = models.OneToOneField(
        'legajos.InscripcionPrograma',
        on_delete=models.PROTECT,
        related_name='instancia_flujo',
        verbose_name='Inscripción',
    )
    version_flujo = models.ForeignKey(
        VersionFlujo,
        on_delete=models.PROTECT,
        related_name='instancias',
        verbose_name='Versión de flujo',
    )
    nodo_actual = models.CharField(
        max_length=255,
        verbose_name='Nodo actual',
        db_index=True,
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVA,
        db_index=True,
        verbose_name='Estado',
    )
    fecha_inicio = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de inicio',
    )
    fecha_cierre = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de cierre',
    )
    datos = models.JSONField(
        default=dict,
        verbose_name='Datos acumulados',
        help_text='Datos recopilados durante la ejecución del flujo',
    )

    class Meta:
        verbose_name = 'Instancia de flujo'
        verbose_name_plural = 'Instancias de flujo'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['version_flujo', 'estado'], name='ix_instflujo_version_estado'),
            models.Index(fields=['estado', 'nodo_actual'], name='ix_instanciaflujo_estado_nodo'),
        ]

    def __str__(self):
        return f'Instancia {self.pk} — {self.inscripcion} ({self.estado})'


class InstanciaLog(models.Model):
    """
    Registro inmutable de cada transición de nodo en una instancia de flujo.
    No se modifica nunca una vez creado.
    """

    instancia = models.ForeignKey(
        InstanciaFlujo,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Instancia',
    )
    nodo_desde = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Nodo origen',
    )
    nodo_hasta = models.CharField(
        max_length=255,
        verbose_name='Nodo destino',
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Timestamp',
        db_index=True,
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transiciones_flujo',
        verbose_name='Usuario',
    )
    motivo = models.TextField(
        blank=True,
        verbose_name='Motivo',
    )
    datos_transicion = models.JSONField(
        default=dict,
        verbose_name='Datos de transición',
    )

    class Meta:
        verbose_name = 'Log de instancia'
        verbose_name_plural = 'Logs de instancia'
        ordering = ['instancia', 'timestamp']
        indexes = [
            models.Index(fields=['instancia', 'timestamp'], name='ix_instancialog_instancia_ts'),
        ]

    def __str__(self):
        return f'Log {self.pk}: {self.nodo_desde} → {self.nodo_hasta}'
