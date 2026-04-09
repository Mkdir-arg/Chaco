"""
Modelos de Auditoría Extendida - Fase 1 (CRÍTICO)
Sistema SEDRONAR - Trazabilidad completa de datos sensibles
"""

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import json


class TipoAccionAuditoria(models.TextChoices):
    """Tipos de acciones auditables"""
    CREATE = "CREATE", "Crear"
    UPDATE = "UPDATE", "Actualizar"
    DELETE = "DELETE", "Eliminar"
    VIEW = "VIEW", "Ver"
    DOWNLOAD = "DOWNLOAD", "Descargar"
    EXPORT = "EXPORT", "Exportar"
    RESTORE = "RESTORE", "Restaurar"


class AuditoriaCiudadano(models.Model):
    """Auditoría completa de cambios en ciudadanos - DATOS SENSIBLES"""
    
    ciudadano = models.ForeignKey(
        'legajos.Ciudadano',
        on_delete=models.SET_NULL,
        related_name='auditorias',
        null=True,
        blank=True
    )
    accion = models.CharField(max_length=20, choices=TipoAccionAuditoria.choices)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Campos modificados con valores anteriores y nuevos
    campos_modificados = models.JSONField(
        blank=True,
        null=True,
        help_text='{"campo": {"anterior": "valor", "nuevo": "valor"}}'
    )
    
    # Snapshot completo antes y después del cambio
    datos_anteriores = models.JSONField(blank=True, null=True)
    datos_nuevos = models.JSONField(blank=True, null=True)
    
    # Información de la sesión
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Justificación del cambio
    motivo = models.TextField(
        blank=True,
        help_text="Justificación del cambio (requerido para datos sensibles)"
    )
    
    # Campos sensibles modificados
    modifico_datos_personales = models.BooleanField(
        default=False,
        help_text="DNI, nombre, apellido modificados"
    )
    
    class Meta:
        verbose_name = "Auditoría de Ciudadano"
        verbose_name_plural = "Auditorías de Ciudadanos"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["ciudadano", "-timestamp"]),
            models.Index(fields=["usuario", "-timestamp"]),
            models.Index(fields=["accion", "-timestamp"]),
            models.Index(fields=["modifico_datos_personales", "-timestamp"]),
        ]
    
    def __str__(self):
        return f"{self.get_accion_display()} - {self.ciudadano} - {self.timestamp}"


class AuditoriaLegajo(models.Model):
    """Auditoría de cambios en legajos de atención"""
    
    legajo = models.ForeignKey(
        'legajos.LegajoAtencion',
        on_delete=models.CASCADE,
        related_name='auditorias'
    )
    accion = models.CharField(max_length=20, choices=TipoAccionAuditoria.choices)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Campo específico modificado
    campo_modificado = models.CharField(
        max_length=100,
        blank=True,
        help_text="estado, responsable, nivel_riesgo, etc."
    )
    valor_anterior = models.TextField(blank=True)
    valor_nuevo = models.TextField(blank=True)
    
    # Snapshot completo
    datos_completos_anteriores = models.JSONField(blank=True, null=True)
    datos_completos_nuevos = models.JSONField(blank=True, null=True)
    
    # Información de la sesión
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Justificación
    motivo = models.TextField(blank=True)
    
    # Flags para cambios importantes
    cambio_estado = models.BooleanField(default=False)
    cambio_responsable = models.BooleanField(default=False)
    cambio_nivel_riesgo = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Auditoría de Legajo"
        verbose_name_plural = "Auditorías de Legajos"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["legajo", "-timestamp"]),
            models.Index(fields=["usuario", "-timestamp"]),
            models.Index(fields=["accion", "-timestamp"]),
            models.Index(fields=["cambio_estado", "-timestamp"]),
            models.Index(fields=["cambio_responsable", "-timestamp"]),
            models.Index(fields=["cambio_nivel_riesgo", "-timestamp"]),
        ]
    
    def __str__(self):
        return f"{self.get_accion_display()} - Legajo {self.legajo.codigo} - {self.timestamp}"


class AuditoriaEvaluacion(models.Model):
    """Auditoría de evaluaciones iniciales - DATOS CLÍNICOS SENSIBLES"""
    
    evaluacion = models.ForeignKey(
        'legajos.EvaluacionInicial',
        on_delete=models.CASCADE,
        related_name='auditorias'
    )
    accion = models.CharField(max_length=20, choices=TipoAccionAuditoria.choices)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Campos modificados
    campos_modificados = models.JSONField(blank=True, null=True)
    datos_anteriores = models.JSONField(blank=True, null=True)
    datos_nuevos = models.JSONField(blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Alertas especiales para cambios críticos
    genera_alerta = models.BooleanField(
        default=False,
        help_text="Genera alerta automática por cambio en riesgo_suicida o violencia"
    )
    cambio_riesgo_suicida = models.BooleanField(default=False)
    cambio_violencia = models.BooleanField(default=False)
    
    # Valores anteriores y nuevos de campos críticos
    riesgo_suicida_anterior = models.BooleanField(null=True, blank=True)
    riesgo_suicida_nuevo = models.BooleanField(null=True, blank=True)
    violencia_anterior = models.BooleanField(null=True, blank=True)
    violencia_nuevo = models.BooleanField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Auditoría de Evaluación"
        verbose_name_plural = "Auditorías de Evaluaciones"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["evaluacion", "-timestamp"]),
            models.Index(fields=["usuario", "-timestamp"]),
            models.Index(fields=["genera_alerta", "-timestamp"]),
            models.Index(fields=["cambio_riesgo_suicida", "-timestamp"]),
            models.Index(fields=["cambio_violencia", "-timestamp"]),
        ]
    
    def __str__(self):
        return f"{self.get_accion_display()} - Evaluación {self.evaluacion.legajo.codigo} - {self.timestamp}"


class AuditoriaEventoCritico(models.Model):
    """Auditoría de eventos críticos - ALTA PRIORIDAD"""
    
    evento = models.ForeignKey(
        'legajos.EventoCritico',
        on_delete=models.CASCADE,
        related_name='auditorias'
    )
    accion = models.CharField(max_length=20, choices=TipoAccionAuditoria.choices)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    datos_anteriores = models.JSONField(blank=True, null=True)
    datos_nuevos = models.JSONField(blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Notificaciones realizadas
    notificados = models.JSONField(
        blank=True,
        null=True,
        help_text="Lista de personas/instituciones notificadas del cambio"
    )
    
    # Tipo de evento para búsquedas rápidas
    tipo_evento = models.CharField(max_length=40, blank=True)
    
    class Meta:
        verbose_name = "Auditoría de Evento Crítico"
        verbose_name_plural = "Auditorías de Eventos Críticos"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["evento", "-timestamp"]),
            models.Index(fields=["usuario", "-timestamp"]),
            models.Index(fields=["tipo_evento", "-timestamp"]),
        ]
    
    def __str__(self):
        return f"{self.get_accion_display()} - Evento {self.evento.tipo} - {self.timestamp}"


class AuditoriaConsentimiento(models.Model):
    """Auditoría de consentimientos informados - REQUISITO LEGAL"""
    
    consentimiento = models.ForeignKey(
        'legajos.Consentimiento',
        on_delete=models.CASCADE,
        related_name='auditorias'
    )
    accion = models.CharField(max_length=20, choices=TipoAccionAuditoria.choices)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    datos_completos = models.JSONField(
        help_text="Snapshot completo del consentimiento"
    )
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Hash del archivo para verificar integridad
    archivo_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="SHA256 del archivo adjunto"
    )
    archivo_nombre = models.CharField(max_length=255, blank=True)
    
    # Justificación obligatoria para DELETE
    motivo = models.TextField(
        help_text="Justificación del cambio (OBLIGATORIO para DELETE)"
    )
    
    # Aprobación para cambios críticos
    aprobado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consentimientos_aprobados',
        help_text="Supervisor que aprobó el cambio"
    )
    
    class Meta:
        verbose_name = "Auditoría de Consentimiento"
        verbose_name_plural = "Auditorías de Consentimientos"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["consentimiento", "-timestamp"]),
            models.Index(fields=["usuario", "-timestamp"]),
            models.Index(fields=["accion", "-timestamp"]),
        ]
    
    def __str__(self):
        return f"{self.get_accion_display()} - Consentimiento {self.consentimiento.id} - {self.timestamp}"


class AuditoriaAccesoSensible(models.Model):
    """Auditoría específica de acceso a datos sensibles"""
    
    class TipoAcceso(models.TextChoices):
        VIEW = "VIEW", "Visualización"
        DOWNLOAD = "DOWNLOAD", "Descarga"
        EXPORT = "EXPORT", "Exportación"
        PRINT = "PRINT", "Impresión"
    
    # Objeto accedido (GenericForeignKey)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=100)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tipo_acceso = models.CharField(max_length=20, choices=TipoAcceso.choices)
    
    # Campos sensibles accedidos
    campos_accedidos = models.JSONField(
        help_text="Lista de campos sensibles que fueron accedidos"
    )
    
    # Información de la sesión
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Justificación del acceso
    justificacion = models.TextField(
        help_text="Motivo del acceso a datos sensibles"
    )
    
    # Contexto del acceso
    url_acceso = models.CharField(max_length=500, blank=True)
    metodo_http = models.CharField(max_length=10, blank=True)
    
    # Flags de alerta
    fuera_horario = models.BooleanField(
        default=False,
        help_text="Acceso fuera del horario laboral (22:00-06:00)"
    )
    acceso_multiple = models.BooleanField(
        default=False,
        help_text="Múltiples accesos en corto tiempo"
    )
    
    class Meta:
        verbose_name = "Auditoría de Acceso Sensible"
        verbose_name_plural = "Auditorías de Accesos Sensibles"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["content_type", "object_id", "-timestamp"]),
            models.Index(fields=["usuario", "-timestamp"]),
            models.Index(fields=["tipo_acceso", "-timestamp"]),
            models.Index(fields=["fuera_horario", "-timestamp"]),
            models.Index(fields=["acceso_multiple", "-timestamp"]),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_acceso_display()} - {self.usuario} - {self.timestamp}"


class AuditoriaDerivacion(models.Model):
    """Auditoría completa de derivaciones"""
    
    derivacion = models.ForeignKey(
        'legajos.Derivacion',
        on_delete=models.CASCADE,
        related_name='auditorias'
    )
    accion = models.CharField(max_length=20, choices=TipoAccionAuditoria.choices)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Estados
    estado_anterior = models.CharField(max_length=20, blank=True)
    estado_nuevo = models.CharField(max_length=20, blank=True)
    
    # Datos completos
    datos_completos = models.JSONField()
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Instituciones involucradas
    institucion_origen = models.ForeignKey(
        'core.Institucion',
        on_delete=models.SET_NULL,
        null=True,
        related_name='auditorias_derivacion_origen'
    )
    institucion_destino = models.ForeignKey(
        'core.Institucion',
        on_delete=models.SET_NULL,
        null=True,
        related_name='auditorias_derivacion_destino'
    )
    
    # Flags
    cambio_estado = models.BooleanField(default=False)
    cambio_urgencia = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Auditoría de Derivación"
        verbose_name_plural = "Auditorías de Derivaciones"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["derivacion", "-timestamp"]),
            models.Index(fields=["usuario", "-timestamp"]),
            models.Index(fields=["cambio_estado", "-timestamp"]),
            models.Index(fields=["institucion_origen", "-timestamp"]),
            models.Index(fields=["institucion_destino", "-timestamp"]),
        ]
    
    def __str__(self):
        return f"{self.get_accion_display()} - Derivación {self.derivacion.id} - {self.timestamp}"


class AuditoriaPlanIntervencion(models.Model):
    """Auditoría de planes de intervención"""
    
    plan = models.ForeignKey(
        'legajos.PlanIntervencion',
        on_delete=models.CASCADE,
        related_name='auditorias'
    )
    accion = models.CharField(max_length=20, choices=TipoAccionAuditoria.choices)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    campos_modificados = models.JSONField(blank=True, null=True)
    datos_anteriores = models.JSONField(blank=True, null=True)
    datos_nuevos = models.JSONField(blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Cambio de vigencia
    cambio_vigencia = models.BooleanField(
        default=False,
        help_text="Cambió el estado de vigencia del plan"
    )
    vigente_anterior = models.BooleanField(null=True, blank=True)
    vigente_nuevo = models.BooleanField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Auditoría de Plan de Intervención"
        verbose_name_plural = "Auditorías de Planes de Intervención"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["plan", "-timestamp"]),
            models.Index(fields=["usuario", "-timestamp"]),
            models.Index(fields=["cambio_vigencia", "-timestamp"]),
        ]
    
    def __str__(self):
        return f"{self.get_accion_display()} - Plan {self.plan.id} - {self.timestamp}"


class AuditoriaInstitucion(models.Model):
    """Auditoría de cambios en instituciones"""
    
    institucion = models.ForeignKey(
        'core.Institucion',
        on_delete=models.CASCADE,
        related_name='auditorias'
    )
    accion = models.CharField(max_length=20, choices=TipoAccionAuditoria.choices)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    campos_modificados = models.JSONField(blank=True, null=True)
    datos_anteriores = models.JSONField(blank=True, null=True)
    datos_nuevos = models.JSONField(blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Cambio de estado de registro
    cambio_estado_registro = models.BooleanField(
        default=False,
        help_text="Cambió el estado de registro de la institución"
    )
    estado_registro_anterior = models.CharField(max_length=15, blank=True)
    estado_registro_nuevo = models.CharField(max_length=15, blank=True)
    
    # Cambio de estado activo
    cambio_activo = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Auditoría de Institución"
        verbose_name_plural = "Auditorías de Instituciones"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["institucion", "-timestamp"]),
            models.Index(fields=["usuario", "-timestamp"]),
            models.Index(fields=["cambio_estado_registro", "-timestamp"]),
            models.Index(fields=["cambio_activo", "-timestamp"]),
        ]
    
    def __str__(self):
        return f"{self.get_accion_display()} - {self.institucion.nombre} - {self.timestamp}"


# Modelo para tracking de cambios masivos
class OperacionMasiva(models.Model):
    """Registro de operaciones masivas (imports, exports, cambios batch)"""
    
    class TipoOperacion(models.TextChoices):
        IMPORT = "IMPORT", "Importación"
        EXPORT = "EXPORT", "Exportación"
        UPDATE_BATCH = "UPDATE_BATCH", "Actualización Masiva"
        DELETE_BATCH = "DELETE_BATCH", "Eliminación Masiva"
    
    tipo = models.CharField(max_length=20, choices=TipoOperacion.choices)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Detalles de la operación
    modelo_afectado = models.CharField(max_length=100)
    cantidad_registros = models.PositiveIntegerField()
    registros_exitosos = models.PositiveIntegerField(default=0)
    registros_fallidos = models.PositiveIntegerField(default=0)
    
    # Archivos
    archivo_origen = models.FileField(upload_to='auditorias/operaciones/', blank=True)
    archivo_log = models.FileField(upload_to='auditorias/logs/', blank=True)
    
    # Timestamps
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    
    # Estado
    completada = models.BooleanField(default=False)
    errores = models.JSONField(blank=True, null=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Operación Masiva"
        verbose_name_plural = "Operaciones Masivas"
        ordering = ["-fecha_inicio"]
        indexes = [
            models.Index(fields=["usuario", "-fecha_inicio"]),
            models.Index(fields=["tipo", "-fecha_inicio"]),
            models.Index(fields=["modelo_afectado", "-fecha_inicio"]),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.modelo_afectado} ({self.cantidad_registros} registros)"
