from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from core.models import TimeStamped, DispositivoRed
from .models import Ciudadano, LegajoAtencion


class TipoContacto(models.TextChoices):
    """Tipos de contacto disponibles"""
    LLAMADA = "LLAMADA", "Llamada Telefónica"
    EMAIL = "EMAIL", "Email"
    VISITA_DOMICILIARIA = "VISITA_DOM", "Visita Domiciliaria"
    REUNION_PRESENCIAL = "REUNION", "Reunión Presencial"
    VIDEOLLAMADA = "VIDEO", "Videollamada"
    MENSAJE = "MENSAJE", "Mensaje/WhatsApp"


class EstadoContacto(models.TextChoices):
    """Estados del contacto"""
    EXITOSO = "EXITOSO", "Exitoso"
    NO_CONTESTA = "NO_CONTESTA", "No contesta"
    OCUPADO = "OCUPADO", "Ocupado"
    CANCELADO = "CANCELADO", "Cancelado"
    REPROGRAMADO = "REPROGRAMADO", "Reprogramado"


class HistorialContacto(TimeStamped):
    """Historial de todos los contactos con el ciudadano"""
    
    legajo = models.ForeignKey(
        LegajoAtencion,
        on_delete=models.CASCADE,
        related_name="historial_contactos"
    )
    tipo_contacto = models.CharField(
        max_length=20,
        choices=TipoContacto.choices
    )
    fecha_contacto = models.DateTimeField()
    duracion_minutos = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Duración en minutos (para llamadas/reuniones)"
    )
    profesional = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="contactos_realizados"
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoContacto.choices,
        default=EstadoContacto.EXITOSO
    )
    motivo = models.CharField(
        max_length=200,
        help_text="Motivo del contacto"
    )
    resumen = models.TextField(
        help_text="Resumen de la conversación/encuentro"
    )
    acuerdos = models.TextField(
        blank=True,
        help_text="Acuerdos alcanzados"
    )
    proximos_pasos = models.TextField(
        blank=True,
        help_text="Próximos pasos acordados"
    )
    participantes = models.TextField(
        blank=True,
        help_text="Otras personas presentes (para reuniones/visitas)"
    )
    ubicacion = models.CharField(
        max_length=200,
        blank=True,
        help_text="Ubicación del encuentro"
    )
    archivo_adjunto = models.FileField(
        upload_to="contactos/",
        blank=True,
        null=True,
        help_text="Grabación, foto, documento relacionado"
    )
    seguimiento_requerido = models.BooleanField(
        default=False,
        help_text="Requiere seguimiento posterior"
    )
    fecha_proximo_contacto = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha sugerida para próximo contacto"
    )
    
    class Meta:
        verbose_name = "Historial de Contacto"
        verbose_name_plural = "Historial de Contactos"
        ordering = ["-fecha_contacto"]
        indexes = [
            models.Index(fields=["legajo", "-fecha_contacto"]),
            models.Index(fields=["tipo_contacto", "estado"]),
            models.Index(fields=["profesional", "-fecha_contacto"]),
            models.Index(fields=["seguimiento_requerido"]),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_contacto_display()} - {self.legajo.ciudadano} ({self.fecha_contacto.date()})"
    
    @property
    def duracion_formateada(self):
        """Retorna la duración en formato legible"""
        if not self.duracion_minutos:
            return "N/A"
        horas = self.duracion_minutos // 60
        minutos = self.duracion_minutos % 60
        if horas > 0:
            return f"{horas}h {minutos}m"
        return f"{minutos}m"


class TipoVinculo(models.TextChoices):
    """Tipos de vínculos familiares"""
    PADRE = "PADRE", "Padre"
    MADRE = "MADRE", "Madre"
    HIJO = "HIJO", "Hijo/a"
    HERMANO = "HERMANO", "Hermano/a"
    ABUELO = "ABUELO", "Abuelo/a"
    TIO = "TIO", "Tío/a"
    PRIMO = "PRIMO", "Primo/a"
    PAREJA = "PAREJA", "Pareja"
    EXPAREJA = "EXPAREJA", "Ex pareja"
    CUÑADO = "CUÑADO", "Cuñado/a"
    YERNO = "YERNO", "Yerno/Nuera"
    SUEGRO = "SUEGRO", "Suegro/a"
    AMIGO = "AMIGO", "Amigo/a"
    VECINO = "VECINO", "Vecino/a"
    REFERENTE = "REFERENTE", "Referente comunitario"
    TUTOR = "TUTOR", "Tutor legal"
    OTRO = "OTRO", "Otro"


class VinculoFamiliar(TimeStamped):
    """Vínculos familiares y referentes del ciudadano"""
    
    ciudadano_principal = models.ForeignKey(
        Ciudadano,
        on_delete=models.CASCADE,
        related_name="vinculos_como_principal"
    )
    ciudadano_vinculado = models.ForeignKey(
        Ciudadano,
        on_delete=models.CASCADE,
        related_name="vinculos_como_vinculado",
        help_text="Debe ser otro ciudadano registrado en el sistema"
    )
    tipo_vinculo = models.CharField(
        max_length=20,
        choices=TipoVinculo.choices
    )
    es_contacto_emergencia = models.BooleanField(
        default=False,
        help_text="Disponible para emergencias 24hs"
    )
    es_referente_tratamiento = models.BooleanField(
        default=False,
        help_text="Participa activamente en el tratamiento"
    )
    convive = models.BooleanField(
        default=False,
        help_text="Vive en el mismo domicilio"
    )
    telefono_alternativo = models.CharField(
        max_length=40,
        blank=True,
        help_text="Teléfono adicional para este vínculo"
    )
    observaciones = models.TextField(
        blank=True,
        help_text="Observaciones sobre la relación"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Vínculo activo"
    )
    
    class Meta:
        verbose_name = "Vínculo Familiar"
        verbose_name_plural = "Vínculos Familiares"
        unique_together = ["ciudadano_principal", "ciudadano_vinculado", "tipo_vinculo"]
        indexes = [
            models.Index(fields=["ciudadano_principal", "activo"]),
            models.Index(fields=["es_contacto_emergencia"]),
            models.Index(fields=["es_referente_tratamiento"]),
        ]
    
    def __str__(self):
        return f"{self.ciudadano_principal} - {self.get_tipo_vinculo_display()}: {self.ciudadano_vinculado}"
    
    def clean(self):
        if self.ciudadano_principal == self.ciudadano_vinculado:
            raise ValidationError("Un ciudadano no puede vincularse consigo mismo")


class RolProfesional(models.TextChoices):
    """Roles de profesionales tratantes"""
    PSICOLOGO = "PSICOLOGO", "Psicólogo/a"
    PSIQUIATRA = "PSIQUIATRA", "Psiquiatra"
    MEDICO = "MEDICO", "Médico/a"
    TRABAJADOR_SOCIAL = "TS", "Trabajador/a Social"
    OPERADOR = "OPERADOR", "Operador/a Socioterapéutico"
    COORDINADOR = "COORDINADOR", "Coordinador/a"
    DIRECTOR = "DIRECTOR", "Director/a"
    ENFERMERO = "ENFERMERO", "Enfermero/a"
    TERAPISTA = "TERAPISTA", "Terapista Ocupacional"
    ABOGADO = "ABOGADO", "Abogado/a"
    OTRO = "OTRO", "Otro"


class ProfesionalTratante(TimeStamped):
    """Profesionales que trabajan con el ciudadano"""
    
    legajo = models.ForeignKey(
        LegajoAtencion,
        on_delete=models.CASCADE,
        related_name="profesionales_tratantes"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        help_text="Usuario del sistema"
    )
    rol = models.CharField(
        max_length=20,
        choices=RolProfesional.choices
    )
    es_responsable_principal = models.BooleanField(
        default=False,
        help_text="Responsable principal del caso"
    )
    dispositivo = models.ForeignKey(
        DispositivoRed,
        on_delete=models.PROTECT,
        help_text="Dispositivo donde trabaja"
    )
    fecha_asignacion = models.DateField(auto_now_add=True)
    fecha_desasignacion = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha cuando dejó de atender el caso"
    )
    activo = models.BooleanField(default=True)
    observaciones = models.TextField(
        blank=True,
        help_text="Observaciones sobre su participación"
    )
    
    class Meta:
        verbose_name = "Profesional Tratante"
        verbose_name_plural = "Profesionales Tratantes"
        unique_together = ["legajo", "usuario", "rol"]
        indexes = [
            models.Index(fields=["legajo", "activo"]),
            models.Index(fields=["usuario", "activo"]),
            models.Index(fields=["es_responsable_principal"]),
        ]
    
    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} - {self.get_rol_display()}"
    
    def clean(self):
        # Solo puede haber un responsable principal activo por legajo
        if self.es_responsable_principal and self.activo:
            existing = ProfesionalTratante.objects.filter(
                legajo=self.legajo,
                es_responsable_principal=True,
                activo=True
            ).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("Ya existe un responsable principal activo para este legajo")


class DispositivoVinculado(TimeStamped):
    """Dispositivos donde el ciudadano está o estuvo admitido"""
    
    class EstadoAdmision(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        EGRESADO = "EGRESADO", "Egresado"
        DERIVADO = "DERIVADO", "Derivado"
        ABANDONO = "ABANDONO", "Abandono"
        SUSPENDIDO = "SUSPENDIDO", "Suspendido"
    
    legajo = models.ForeignKey(
        LegajoAtencion,
        on_delete=models.CASCADE,
        related_name="dispositivos_vinculados"
    )
    dispositivo = models.ForeignKey(
        DispositivoRed,
        on_delete=models.PROTECT
    )
    fecha_admision = models.DateField()
    fecha_egreso = models.DateField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadoAdmision.choices,
        default=EstadoAdmision.ACTIVO
    )
    referente_dispositivo = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Referente en el dispositivo"
    )
    observaciones = models.TextField(
        blank=True,
        help_text="Observaciones sobre la admisión"
    )
    
    class Meta:
        verbose_name = "Dispositivo Vinculado"
        verbose_name_plural = "Dispositivos Vinculados"
        unique_together = ["legajo", "dispositivo", "fecha_admision"]
        indexes = [
            models.Index(fields=["legajo", "estado"]),
            models.Index(fields=["dispositivo", "estado"]),
        ]
    
    def __str__(self):
        return f"{self.legajo.ciudadano} en {self.dispositivo.nombre}"


class ContactoEmergencia(TimeStamped):
    """Contactos específicos para emergencias"""
    
    legajo = models.ForeignKey(
        LegajoAtencion,
        on_delete=models.CASCADE,
        related_name="contactos_emergencia"
    )
    nombre = models.CharField(max_length=120)
    relacion = models.CharField(
        max_length=100,
        help_text="Relación con el ciudadano"
    )
    telefono_principal = models.CharField(max_length=40)
    telefono_alternativo = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    disponibilidad_24hs = models.BooleanField(
        default=True,
        help_text="Disponible las 24 horas"
    )
    prioridad = models.PositiveSmallIntegerField(
        default=1,
        help_text="Orden de prioridad (1=mayor prioridad)"
    )
    instrucciones_especiales = models.TextField(
        blank=True,
        help_text="Instrucciones especiales para contactar"
    )
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Contacto de Emergencia"
        verbose_name_plural = "Contactos de Emergencia"
        ordering = ["prioridad", "nombre"]
        indexes = [
            models.Index(fields=["legajo", "activo", "prioridad"]),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.relacion}) - Prioridad {self.prioridad}"