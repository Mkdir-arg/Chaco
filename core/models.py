from uuid import uuid4
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


def generate_codigo():
    """Genera un código único para legajos"""
    return str(uuid4())


class Provincia(models.Model):
    """
    Guardado de las provincias de los vecinos y vecinas registrados.
    """

    nombre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return str(self.nombre)

    class Meta:
        ordering = ["id"]
        verbose_name = "Provincia"
        verbose_name_plural = "Provincia"


class Mes(models.Model):

    nombre = models.CharField(max_length=255)

    def __str__(self):
        return str(self.nombre)

    class Meta:
        ordering = ["id"]
        verbose_name = "Mes"
        verbose_name_plural = "Meses"


class Dia(models.Model):

    nombre = models.CharField(max_length=255)

    def __str__(self):
        return str(self.nombre)

    class Meta:
        ordering = ["id"]
        verbose_name = "Dia"
        verbose_name_plural = "Dias"


class Turno(models.Model):

    nombre = models.CharField(max_length=255)

    def __str__(self):
        return str(self.nombre)

    class Meta:
        ordering = ["id"]
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"


class Municipio(models.Model):
    """
    Guardado de los municipios de los vecinos y vecinas registrados.
    """

    nombre = models.CharField(max_length=255)
    provincia = models.ForeignKey(
        Provincia, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return str(self.nombre)

    class Meta:
        ordering = ["id"]
        verbose_name = "Municipio"
        verbose_name_plural = "Municipio"
        unique_together = (
            "nombre",
            "provincia",
        )


class Localidad(models.Model):
    """
    Guardado de las localidades de los vecinos y vecinas registrados.
    """

    nombre = models.CharField(max_length=255)
    municipio = models.ForeignKey(
        Municipio, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return str(self.nombre)

    class Meta:
        verbose_name = "Localidad"
        verbose_name_plural = "Localidad"
        unique_together = (
            "nombre",
            "municipio",
        )


class Sexo(models.Model):
    sexo = models.CharField(max_length=10)

    def __str__(self):
        return str(self.sexo)

    class Meta:
        verbose_name = "Sexo"
        verbose_name_plural = "Sexos"


# Modelos base para sistema de legajos
class TimeStamped(models.Model):
    """Modelo abstracto para timestamps automáticos"""
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class LegajoBase(TimeStamped):
    """Modelo base abstracto para todos los tipos de legajos"""
    
    class Estado(models.TextChoices):
        ABIERTO = "ABIERTO", "Abierto"
        EN_SEGUIMIENTO = "EN_SEGUIMIENTO", "En seguimiento"
        DERIVADO = "DERIVADO", "Derivado"
        CERRADO = "CERRADO", "Cerrado"
    
    class Confidencialidad(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        RESTRINGIDA = "RESTRINGIDA", "Restringida"
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    codigo = models.CharField(max_length=36, unique=True, default=generate_codigo)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ABIERTO)
    fecha_apertura = models.DateField(auto_now_add=True)
    fecha_cierre = models.DateField(null=True, blank=True)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name="legajos_responsable"
    )
    confidencialidad = models.CharField(
        max_length=20, 
        choices=Confidencialidad.choices, 
        default=Confidencialidad.NORMAL
    )
    notas = models.TextField(blank=True)
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["estado"]),
            models.Index(fields=["fecha_apertura"]),
            models.Index(fields=["responsable"]),
        ]


class TipoInstitucion(models.TextChoices):
    """Tipos de instituciones registradas en SEDRONAR"""
    DTC = "DTC", "Dispositivo Territorial Comunitario"
    CAAC = "CAAC", "Casa de Atención y Acompañamiento Comunitario"
    CCC = "CCC", "Casa Comunitaria Convivencial"
    CAI = "CAI", "Centro de Asistencia Inmediata"
    IC = "IC", "Institución Conveniada"
    CT = "CT", "Comunidad Terapéutica"


class EstadoRegistro(models.TextChoices):
    """Estados del proceso de registro"""
    BORRADOR = "BORRADOR", "Borrador"
    ENVIADO = "ENVIADO", "Enviado"
    REVISION = "REVISION", "En Revisión"
    OBSERVADO = "OBSERVADO", "Observado"
    APROBADO = "APROBADO", "Aprobado"
    RECHAZADO = "RECHAZADO", "Rechazado"


class TipoPersoneria(models.TextChoices):
    """Tipos de personería jurídica"""
    ASOCIACION_CIVIL = "ASOCIACION_CIVIL", "Asociación Civil"
    FUNDACION = "FUNDACION", "Fundación"
    SOCIEDAD_CIVIL = "SOCIEDAD_CIVIL", "Sociedad Civil"
    SOCIEDAD_COMERCIAL = "SOCIEDAD_COMERCIAL", "Sociedad Comercial"
    ENTIDAD_PUBLICA = "ENTIDAD_PUBLICA", "Entidad Pública"
    OTRO = "OTRO", "Otro"


class Institucion(TimeStamped):
    """Instituciones registradas en la red SEDRONAR"""
    
    # Información básica
    tipo = models.CharField(max_length=15, choices=TipoInstitucion.choices, db_index=True)
    nombre = models.CharField(max_length=180, db_index=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT, db_index=True)
    municipio = models.ForeignKey(Municipio, on_delete=models.PROTECT, db_index=True)
    localidad = models.ForeignKey(Localidad, on_delete=models.PROTECT, null=True, blank=True)
    direccion = models.CharField(max_length=240, blank=True)
    telefono = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True, db_index=True)
    activo = models.BooleanField(default=True, db_index=True)
    descripcion = models.TextField(blank=True)
    
    # Estado del registro
    estado_registro = models.CharField(
        max_length=15, 
        choices=EstadoRegistro.choices, 
        default=EstadoRegistro.BORRADOR,
        db_index=True
    )
    fecha_solicitud = models.DateField(null=True, blank=True)
    fecha_aprobacion = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    
    # Información legal
    tipo_personeria = models.CharField(
        max_length=20, 
        choices=TipoPersoneria.choices, 
        blank=True
    )
    nro_personeria = models.CharField(max_length=80, blank=True)
    fecha_personeria = models.DateField(null=True, blank=True)
    cuit = models.CharField(max_length=15, blank=True)
    
    # Registro SEDRONAR
    nro_registro = models.CharField(max_length=80, blank=True)
    resolucion = models.CharField(max_length=120, blank=True)
    fecha_alta = models.DateField(auto_now_add=True)
    
    # Responsables
    encargados = models.ManyToManyField(
        'auth.User',
        blank=True,
        limit_choices_to={'groups__name': 'EncargadoInstitucion'},
        related_name='instituciones_encargadas',
        verbose_name='Encargados de la Institución'
    )
    
    # Configuración de turnos (opcional)
    configuracion_turnos = models.OneToOneField(
        'turnos.ConfiguracionTurnos',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='institucion',
        verbose_name='Configuración de turnos',
    )

    # Información adicional para asistencia
    presta_asistencia = models.BooleanField(
        default=False,
        verbose_name="Presta servicios de asistencia"
    )
    convenio_obras_sociales = models.BooleanField(
        default=False,
        verbose_name="Tiene convenio con Obras Sociales"
    )
    nro_sss = models.CharField(
        max_length=80, 
        blank=True,
        verbose_name="Número SSS"
    )
    
    class Meta:
        verbose_name = "Institución"
        verbose_name_plural = "Instituciones"
        indexes = [
            models.Index(fields=["tipo", "activo"]),
            models.Index(fields=["provincia", "municipio"]),
            models.Index(fields=["nombre"]),
            models.Index(fields=["estado_registro"]),
            models.Index(fields=["nro_registro"]),
            models.Index(fields=["activo", "tipo", "provincia"]),
            models.Index(fields=["estado_registro", "tipo"]),
        ]
        unique_together = ("nombre", "municipio", "tipo")
    
    def __str__(self):
        return f"{self.nombre} [{self.get_tipo_display()}]"
    
    @property
    def puede_aprobar(self):
        """Verifica si la institución puede ser aprobada"""
        return self.estado_registro in [EstadoRegistro.ENVIADO, EstadoRegistro.REVISION]
    
    def aprobar(self, nro_registro=None, resolucion=None):
        """Aprueba el registro de la institución"""
        if not self.puede_aprobar:
            raise ValidationError("La institución debe estar en estado ENVIADO o REVISION para ser aprobada")
        
        self.estado_registro = EstadoRegistro.APROBADO
        self.fecha_aprobacion = timezone.now().date()
        if nro_registro:
            self.nro_registro = nro_registro
        if resolucion:
            self.resolucion = resolucion
        self.save()
    
    def rechazar(self, motivo):
        """Rechaza el registro de la institución"""
        self.estado_registro = EstadoRegistro.RECHAZADO
        self.observaciones = motivo
        self.save()


# Alias para compatibilidad hacia atrás
DispositivoRed = Institucion
DispositivoTipo = TipoInstitucion


class DocumentoRequerido(TimeStamped):
    """Documentos requeridos para el registro de instituciones"""
    
    class TipoDocumento(models.TextChoices):
        PERSONERIA_JURIDICA = "PERSONERIA_JURIDICA", "Personería Jurídica"
        ESTATUTO = "ESTATUTO", "Estatuto"
        ACTA_ASAMBLEA = "ACTA_ASAMBLEA", "Acta última Asamblea"
        CONTRATO_SOCIETARIO = "CONTRATO_SOCIETARIO", "Contrato Societario"
        ACTA_CONSTITUCION = "ACTA_CONSTITUCION", "Acta de Constitución"
        HABILITACION_MUNICIPAL = "HABILITACION_MUNICIPAL", "Habilitación Municipal"
        PLANOS = "PLANOS", "Planos"
        CONSTANCIA_AFIP = "CONSTANCIA_AFIP", "Constancia AFIP"
        TITULO_PROPIEDAD = "TITULO_PROPIEDAD", "Título de Propiedad/Contrato"
        REGLAMENTO_INTERNO = "REGLAMENTO_INTERNO", "Reglamento Interno"
        SEGUROS = "SEGUROS", "Seguros de Responsabilidad Civil"
        BALANCE = "BALANCE", "Último Balance"
        MATRICULACION = "MATRICULACION", "Matriculación Directivos"
        RECURSOS_HUMANOS = "RECURSOS_HUMANOS", "Listado Recursos Humanos"
        PROGRAMAS = "PROGRAMAS", "Programas Preventivos/Asistenciales"
        ORGANIGRAMA = "ORGANIGRAMA", "Organigrama"
        REGISTRO_BIEN_PUBLICO = "REGISTRO_BIEN_PUBLICO", "Registro Entidad Bien Público"
        CONSTANCIA_SSS = "CONSTANCIA_SSS", "Constancia SSS"
        HABILITACION_SANITARIA = "HABILITACION_SANITARIA", "Habilitación Sanitaria"
        CONVENIO_EMERGENCIA = "CONVENIO_EMERGENCIA", "Convenio Centro Emergencia"
        CONVENIO_SANITARIO = "CONVENIO_SANITARIO", "Convenio Centro Sanitario"
    
    class EstadoDocumento(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        CARGADO = "CARGADO", "Cargado"
        APROBADO = "APROBADO", "Aprobado"
        OBSERVADO = "OBSERVADO", "Observado"
    
    institucion = models.ForeignKey(
        Institucion, 
        on_delete=models.CASCADE, 
        related_name="documentos"
    )
    tipo = models.CharField(max_length=30, choices=TipoDocumento.choices)
    archivo = models.FileField(upload_to="documentos_instituciones/", blank=True)
    estado = models.CharField(
        max_length=15, 
        choices=EstadoDocumento.choices, 
        default=EstadoDocumento.PENDIENTE
    )
    observaciones = models.TextField(blank=True)
    obligatorio = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Documento Requerido"
        verbose_name_plural = "Documentos Requeridos"
        unique_together = ("institucion", "tipo")
        indexes = [
            models.Index(fields=["institucion", "estado"]),
            models.Index(fields=["tipo", "obligatorio"]),
            models.Index(fields=["estado", "obligatorio"]),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.institucion.nombre}"


# Re-exportar para que `from core.models import Secretaria` funcione
from .models_secretaria import Secretaria, Subsecretaria  # noqa: E402, F401
