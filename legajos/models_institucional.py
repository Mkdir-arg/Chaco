"""
Modelos para el Sistema NODO - Gestión Programática Institucional
Versión 3.0 - Unificación con modelo Programa
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
from core.models import TimeStamped, Institucion
from .models_programas import Programa


# ============================================================================
# ENUMS Y CHOICES
# ============================================================================

class EstadoDerivacion(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    ACEPTADA = 'ACEPTADA', 'Aceptada'
    RECHAZADA = 'RECHAZADA', 'Rechazada'
    ACEPTADA_UNIFICADA = 'ACEPTADA_UNIFICADA', 'Aceptada Unificada'


class EstadoCaso(models.TextChoices):
    ACTIVO = 'ACTIVO', 'Activo'
    EN_SEGUIMIENTO = 'EN_SEGUIMIENTO', 'En Seguimiento'
    SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'
    EGRESADO = 'EGRESADO', 'Egresado'
    CERRADO = 'CERRADO', 'Cerrado'


class EstadoPrograma(models.TextChoices):
    ACTIVO = 'ACTIVO', 'Activo'
    SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'
    CERRADO = 'CERRADO', 'Cerrado'


class EstadoGlobal(models.TextChoices):
    ACTIVO = 'ACTIVO', 'Activo'
    OBSERVACION = 'OBSERVACION', 'En Observación'
    SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'
    CERRADO = 'CERRADO', 'Cerrado'


class UrgenciaDerivacion(models.TextChoices):
    BAJA = 'BAJA', 'Baja'
    MEDIA = 'MEDIA', 'Media'
    ALTA = 'ALTA', 'Alta'


class TipoInicioDerivacion(models.TextChoices):
    DERIVACION = 'DERIVACION', 'Derivación'
    INSCRIPCION_DIRECTA = 'INSCRIPCION_DIRECTA', 'Inscripción Directa'


class EstadoDerivacionCiudadano(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    ACEPTADA = 'ACEPTADA', 'Aceptada'
    RECHAZADA = 'RECHAZADA', 'Rechazada'


class RolUsuarioPrograma(models.TextChoices):
    RESPONSABLE_LOCAL = 'RESPONSABLE_LOCAL', 'Responsable Local'
    COORDINADOR = 'COORDINADOR', 'Coordinador'
    OPERADOR = 'OPERADOR', 'Operador'
    STAFF = 'STAFF', 'Staff'


# ============================================================================
# MODELOS PRINCIPALES
# ============================================================================

class InstitucionPrograma(TimeStamped):
    """
    Relación N:N contextualizada entre Institución y Programa.
    Define que una institución está habilitada para ejecutar un programa específico.
    """
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.CASCADE,
        related_name='programas_habilitados'
    )
    programa = models.ForeignKey(
        Programa,
        on_delete=models.PROTECT,
        related_name='instituciones_habilitadas'
    )
    
    # Estado programático
    estado_programa = models.CharField(
        max_length=20,
        choices=EstadoPrograma.choices,
        default=EstadoPrograma.ACTIVO,
        db_index=True
    )
    activo = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Si False, no se muestra solapa en UI"
    )
    
    # Control de cupo
    cupo_maximo = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Capacidad máxima de casos simultáneos"
    )
    controlar_cupo = models.BooleanField(
        default=False,
        help_text="Si True, valida cupo al aceptar derivaciones"
    )
    permite_sobrecupo = models.BooleanField(
        default=False,
        help_text="Si True, permite aceptar derivaciones con cupo lleno"
    )
    
    # Responsable local del programa
    responsable_local = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='institucion_programas_responsable'
    )
    
    # Fechas
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Institución-Programa"
        verbose_name_plural = "Instituciones-Programas"
        unique_together = ['institucion', 'programa']
        indexes = [
            models.Index(fields=['institucion', 'activo']),
            models.Index(fields=['programa', 'estado_programa']),
            models.Index(fields=['estado_programa', 'activo']),
        ]
    
    def __str__(self):
        return f"{self.institucion.nombre} - {self.programa.nombre}"
    
    def clean(self):
        if self.controlar_cupo and self.cupo_maximo is None:
            raise ValidationError({
                'cupo_maximo': 'Si controla cupo, debe especificar cupo_maximo'
            })
    
    @property
    def puede_aceptar_derivaciones(self):
        """Verifica si puede aceptar nuevas derivaciones"""
        # Validar estado global de la institución
        if hasattr(self.institucion, 'legajo_institucional'):
            if self.institucion.legajo_institucional.estado_global == EstadoGlobal.CERRADO:
                return False
        
        # Validar estado programático
        return self.estado_programa == EstadoPrograma.ACTIVO and self.activo
    
    @property
    def casos_activos_count(self):
        """Cantidad de casos activos"""
        return self.casos.filter(
            estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO]
        ).count()
    
    @property
    def cupo_disponible(self):
        """Cupo disponible (None si no controla cupo)"""
        if not self.controlar_cupo or self.cupo_maximo is None:
            return None
        return max(0, self.cupo_maximo - self.casos_activos_count)


class DerivacionInstitucional(TimeStamped):
    """
    Derivación programática de un ciudadano a una institución específica
    dentro de un programa determinado.
    
    Incluye redundancia estratégica para BI y reportes históricos.
    """
    # Relaciones principales
    ciudadano = models.ForeignKey(
        'legajos.Ciudadano',
        on_delete=models.CASCADE,
        related_name='derivaciones_institucionales_legacy'
    )

    # Redundancia estratégica para BI
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.PROTECT,
        related_name='derivaciones_recibidas_legacy'
    )
    programa = models.ForeignKey(
        Programa,
        on_delete=models.PROTECT,
        related_name='derivaciones_programa_legacy'
    )

    # Relación operativa
    institucion_programa = models.ForeignKey(
        InstitucionPrograma,
        on_delete=models.PROTECT,
        related_name='derivaciones_legacy'
    )
    
    # Estado y flujo
    estado = models.CharField(
        max_length=25,
        choices=EstadoDerivacion.choices,
        default=EstadoDerivacion.PENDIENTE,
        db_index=True
    )
    urgencia = models.CharField(
        max_length=10,
        choices=UrgenciaDerivacion.choices,
        default=UrgenciaDerivacion.MEDIA,
        db_index=True
    )
    
    # Datos de la derivación
    motivo = models.TextField()
    observaciones = models.TextField(blank=True)
    
    # Usuario que deriva
    derivado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='derivaciones_institucionales_realizadas_legacy'
    )

    # Respuesta
    respuesta = models.TextField(blank=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True, db_index=True)
    respondido_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derivaciones_institucionales_respondidas_legacy'
    )

    # Caso creado (si aplica)
    caso_creado = models.ForeignKey(
        'CasoInstitucional',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derivacion_creadora_legacy'
    )
    
    class Meta:
        verbose_name = "Derivación Institucional"
        verbose_name_plural = "Derivaciones Institucionales"
        ordering = ['-creado']
        indexes = [
            models.Index(fields=['ciudadano', 'estado']),
            models.Index(fields=['institucion_programa', 'estado']),
            models.Index(fields=['estado', 'urgencia']),
            models.Index(fields=['institucion', 'programa']),
        ]
    
    def __str__(self):
        return f"{self.ciudadano.nombre_completo} → {self.institucion.nombre} ({self.programa.nombre})"
    
    def save(self, *args, **kwargs):
        # Sincronizar redundancia
        if self.institucion_programa:
            self.institucion = self.institucion_programa.institucion
            self.programa = self.institucion_programa.programa
        super().save(*args, **kwargs)


class CasoInstitucional(TimeStamped):
    """
    Instancia operativa de un ciudadano dentro de un programa en una institución.
    
    Representa el caso activo de atención programática.
    Incluye versionado para reaperturas y constraint de unicidad condicional.
    """
    ciudadano = models.ForeignKey(
        'legajos.Ciudadano',
        on_delete=models.CASCADE,
        related_name='casos_institucionales'
    )
    institucion_programa = models.ForeignKey(
        InstitucionPrograma,
        on_delete=models.PROTECT,
        related_name='casos'
    )
    
    # Identificación
    codigo = models.CharField(
        max_length=100,
        unique=True,
        editable=False
    )
    version = models.PositiveIntegerField(
        default=1,
        help_text="Versión del caso (para reaperturas)"
    )
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=EstadoCaso.choices,
        default=EstadoCaso.ACTIVO,
        db_index=True
    )
    
    # Fechas
    fecha_apertura = models.DateField(auto_now_add=True, db_index=True)
    fecha_cierre = models.DateField(null=True, blank=True, db_index=True)
    
    # Responsable
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='casos_institucionales_responsable'
    )
    
    # Observaciones
    observaciones = models.TextField(blank=True)

    # Derivación que originó este caso (nullable — casos históricos no la tienen)
    derivacion_origen = models.ForeignKey(
        'DerivacionCiudadano',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='caso_originado',
        verbose_name='Derivación de origen',
    )

    class Meta:
        verbose_name = "Caso Institucional"
        verbose_name_plural = "Casos Institucionales"
        unique_together = ['ciudadano', 'institucion_programa', 'version']
        indexes = [
            models.Index(fields=['ciudadano', 'estado']),
            models.Index(fields=['institucion_programa', 'estado']),
            models.Index(fields=['estado', 'fecha_apertura']),
            models.Index(fields=['responsable', 'estado']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.ciudadano.nombre_completo}"
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            from datetime import datetime
            self.codigo = f"CASO-{self.institucion_programa.programa.tipo[:3]}-{datetime.now().strftime('%Y%m%d')}-{self.ciudadano.id:05d}"
        super().save(*args, **kwargs)
    
    @property
    def dias_activo(self):
        """Días desde la apertura"""
        from datetime import datetime
        if self.fecha_cierre:
            return (self.fecha_cierre - self.fecha_apertura).days
        return (datetime.now().date() - self.fecha_apertura).days



class DerivacionCiudadano(TimeStamped):
    """
    Modelo unificado de derivación. Reemplaza a DerivacionInstitucional.
    Soporta derivación desde cualquier operador e inscripción directa por gestores.
    """
    ciudadano = models.ForeignKey(
        'legajos.Ciudadano',
        on_delete=models.CASCADE,
        related_name='derivaciones_ciudadanos'
    )
    tipo_inicio = models.CharField(
        max_length=25,
        choices=TipoInicioDerivacion.choices,
        default=TipoInicioDerivacion.DERIVACION
    )

    # Destino — al menos uno debe tener valor
    institucion_programa = models.ForeignKey(
        InstitucionPrograma,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='derivaciones'
    )
    actividad_destino = models.ForeignKey(
        'legajos.PlanFortalecimiento',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='derivaciones_ciudadanos'
    )

    # Redundancia BI (auto en save)
    programa_origen = models.ForeignKey(
        Programa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derivaciones_originadas'
    )
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='derivaciones_ciudadanos_recibidas'
    )
    programa = models.ForeignKey(
        Programa,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='derivaciones_ciudadanos'
    )

    estado = models.CharField(
        max_length=20,
        choices=EstadoDerivacionCiudadano.choices,
        default=EstadoDerivacionCiudadano.PENDIENTE,
        db_index=True
    )
    urgencia = models.CharField(
        max_length=10,
        choices=UrgenciaDerivacion.choices,
        default=UrgenciaDerivacion.MEDIA,
        db_index=True
    )

    motivo = models.TextField()
    observaciones = models.TextField(blank=True)

    derivado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='derivaciones_ciudadanos_realizadas'
    )
    respuesta = models.TextField(blank=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True, db_index=True)
    quien_responde = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derivaciones_ciudadanos_respondidas'
    )

    caso_creado = models.ForeignKey(
        'CasoInstitucional',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derivacion_ciudadano_creadora'
    )
    inscripcion_creada = models.OneToOneField(
        'legajos.InscripcionPrograma',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derivacion_ciudadano_origen'
    )

    class Meta:
        verbose_name = 'Derivación Ciudadano'
        verbose_name_plural = 'Derivaciones Ciudadano'
        ordering = ['-creado']
        indexes = [
            models.Index(fields=['ciudadano', 'estado']),
            models.Index(fields=['institucion_programa', 'estado']),
            models.Index(fields=['estado', 'urgencia']),
            models.Index(fields=['institucion', 'programa']),
        ]

    def __str__(self):
        destino = str(self.institucion_programa) if self.institucion_programa else str(self.actividad_destino)
        return f"{self.ciudadano.nombre_completo} → {destino}"

    def save(self, *args, **kwargs):
        if self.institucion_programa:
            self.institucion = self.institucion_programa.institucion
            self.programa = self.institucion_programa.programa
        super().save(*args, **kwargs)


class CoordinadorPrograma(TimeStamped):
    """
    Relaciona usuarios con programas que coordinan.
    Permite gestión operativa del programa a nivel sistema.
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='programas_coordinados'
    )
    programa = models.ForeignKey(
        Programa,
        on_delete=models.CASCADE,
        related_name='coordinadores'
    )
    activo = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Si False, el usuario pierde acceso al programa"
    )
    
    class Meta:
        verbose_name = "Coordinador de Programa"
        verbose_name_plural = "Coordinadores de Programas"
        unique_together = ['usuario', 'programa']
        indexes = [
            models.Index(fields=['usuario', 'activo']),
            models.Index(fields=['programa', 'activo']),
        ]
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.programa.nombre}"

