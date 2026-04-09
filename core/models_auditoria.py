from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import json


class LogAccion(models.Model):
    """Log de todas las acciones del usuario"""
    
    class TipoAccion(models.TextChoices):
        LOGIN = "LOGIN", "Inicio de sesión"
        LOGOUT = "LOGOUT", "Cierre de sesión"
        CREATE = "CREATE", "Crear"
        UPDATE = "UPDATE", "Actualizar"
        DELETE = "DELETE", "Eliminar"
        VIEW = "VIEW", "Ver"
        DOWNLOAD = "DOWNLOAD", "Descargar"
        EXPORT = "EXPORT", "Exportar"
        IMPORT = "IMPORT", "Importar"
    
    usuario = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    accion = models.CharField(max_length=20, choices=TipoAccion.choices)
    modelo = models.CharField(max_length=100, blank=True)
    objeto_id = models.CharField(max_length=100, blank=True)
    objeto_repr = models.CharField(max_length=200, blank=True)
    detalles = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Log de Acción"
        verbose_name_plural = "Logs de Acciones"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["usuario", "-timestamp"]),
            models.Index(fields=["accion", "-timestamp"]),
            models.Index(fields=["modelo", "-timestamp"]),
        ]
    
    def __str__(self):
        return f"{self.usuario} - {self.get_accion_display()} - {self.timestamp}"


class LogDescargaArchivo(models.Model):
    """Log específico para descargas de archivos"""
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    archivo_nombre = models.CharField(max_length=255)
    archivo_path = models.CharField(max_length=500)
    modelo_origen = models.CharField(max_length=100, blank=True)
    objeto_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Log de Descarga"
        verbose_name_plural = "Logs de Descargas"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["usuario", "-timestamp"]),
            models.Index(fields=["archivo_nombre"]),
        ]
    
    def __str__(self):
        return f"{self.usuario} descargó {self.archivo_nombre}"


class SesionUsuario(models.Model):
    """Tracking de sesiones de usuario"""
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    inicio_sesion = models.DateTimeField(auto_now_add=True)
    ultima_actividad = models.DateTimeField(auto_now=True)
    fin_sesion = models.DateTimeField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Sesión de Usuario"
        verbose_name_plural = "Sesiones de Usuario"
        ordering = ["-inicio_sesion"]
        indexes = [
            models.Index(fields=["usuario", "-inicio_sesion"]),
            models.Index(fields=["activa", "-ultima_actividad"]),
        ]
    
    def __str__(self):
        return f"Sesión {self.usuario} - {self.inicio_sesion}"
    
    @property
    def duracion(self):
        """Duración de la sesión"""
        fin = self.fin_sesion or timezone.now()
        return fin - self.inicio_sesion


class AlertaAuditoria(models.Model):
    """Alertas automáticas del sistema de auditoría"""
    
    class TipoAlerta(models.TextChoices):
        MULTIPLES_LOGINS = "MULTIPLES_LOGINS", "Múltiples inicios de sesión"
        ACTIVIDAD_SOSPECHOSA = "ACTIVIDAD_SOSPECHOSA", "Actividad sospechosa"
        DESCARGA_MASIVA = "DESCARGA_MASIVA", "Descarga masiva de archivos"
        ACCESO_FUERA_HORARIO = "ACCESO_FUERA_HORARIO", "Acceso fuera de horario"
        CAMBIOS_CRITICOS = "CAMBIOS_CRITICOS", "Cambios en datos críticos"
    
    class Severidad(models.TextChoices):
        BAJA = "BAJA", "Baja"
        MEDIA = "MEDIA", "Media"
        ALTA = "ALTA", "Alta"
        CRITICA = "CRITICA", "Crítica"
    
    tipo = models.CharField(max_length=30, choices=TipoAlerta.choices)
    severidad = models.CharField(max_length=10, choices=Severidad.choices)
    usuario_afectado = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="alertas_auditoria"
    )
    descripcion = models.TextField()
    detalles = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    revisada = models.BooleanField(default=False)
    revisada_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="alertas_revisadas"
    )
    fecha_revision = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Alerta de Auditoría"
        verbose_name_plural = "Alertas de Auditoría"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["usuario_afectado", "-timestamp"]),
            models.Index(fields=["tipo", "severidad"]),
            models.Index(fields=["revisada", "-timestamp"]),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.usuario_afectado}"
    
    def marcar_revisada(self, usuario):
        """Marcar alerta como revisada"""
        self.revisada = True
        self.revisada_por = usuario
        self.fecha_revision = timezone.now()
        self.save()