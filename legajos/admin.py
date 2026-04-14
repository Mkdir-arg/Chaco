from django.contrib import admin
from .models import Ciudadano, Profesional, Consentimiento, EvaluacionInicial, Objetivo, PlanIntervencion, SeguimientoContacto, Derivacion, EventoCritico, Adjunto, AlertaEventoCritico
from .models_programas import Programa, InscripcionPrograma, DerivacionPrograma
from .models_institucional import (
    InstitucionPrograma,
    DerivacionCiudadano,
    DerivacionInstitucional,
    CasoInstitucional,
    CoordinadorPrograma,
)


@admin.register(Ciudadano)
class CiudadanoAdmin(admin.ModelAdmin):
    list_display = ("dni", "apellido", "nombre", "activo", "creado")
    search_fields = ("dni", "apellido", "nombre")
    list_filter = ("activo", "genero")
    ordering = ("apellido", "nombre")
    readonly_fields = ("creado", "modificado")
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('legajos__dispositivo')
    
    fieldsets = (
        ("Información Personal", {
            "fields": ("dni", "nombre", "apellido", "fecha_nacimiento", "genero")
        }),
        ("Contacto", {
            "fields": ("telefono", "email", "domicilio")
        }),
        ("Estado", {
            "fields": ("activo",)
        }),
        ("Auditoría", {
            "fields": ("creado", "modificado"),
            "classes": ("collapse",)
        }),
    )


@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rol", "matricula")
    search_fields = ("usuario__username", "usuario__first_name", "usuario__last_name", "rol", "matricula")
    list_filter = ("rol",)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')

@admin.register(Consentimiento)
class ConsentimientoAdmin(admin.ModelAdmin):
    list_display = ("ciudadano", "firmado_por", "fecha_firma", "vigente")
    list_filter = ("vigente", "fecha_firma")
    search_fields = ("ciudadano__dni", "ciudadano__apellido", "ciudadano__nombre")
    readonly_fields = ("creado", "modificado")
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ciudadano')


@admin.register(EvaluacionInicial)
class EvaluacionInicialAdmin(admin.ModelAdmin):
    list_display = ("legajo", "riesgo_suicida", "violencia", "creado")
    list_filter = ("riesgo_suicida", "violencia", "creado")
    search_fields = ("legajo__codigo", "legajo__ciudadano__dni", "legajo__ciudadano__apellido")
    readonly_fields = ("creado", "modificado")
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('legajo__ciudadano', 'legajo__dispositivo')
    
    fieldsets = (
        ("Información Básica", {
            "fields": ("legajo",)
        }),
        ("Evaluación Clínica", {
            "fields": ("situacion_consumo", "antecedentes")
        }),
        ("Evaluación Psicosocial", {
            "fields": ("red_apoyo", "condicion_social")
        }),
        ("Tamizajes y Riesgos", {
            "fields": ("tamizajes", "riesgo_suicida", "violencia")
        }),
        ("Auditoría", {
            "fields": ("creado", "modificado"),
            "classes": ("collapse",)
        }),
    )


@admin.register(Objetivo)
class ObjetivoAdmin(admin.ModelAdmin):
    list_display = ['descripcion', 'legajo', 'cumplido']
    list_filter = ['cumplido']
    search_fields = ['descripcion', 'legajo__codigo']


@admin.register(PlanIntervencion)
class PlanIntervencionAdmin(admin.ModelAdmin):
    list_display = ['legajo', 'profesional', 'vigente', 'creado']
    list_filter = ['vigente', 'creado']
    search_fields = ['legajo__codigo']


@admin.register(SeguimientoContacto)
class SeguimientoContactoAdmin(admin.ModelAdmin):
    list_display = ['legajo', 'tipo', 'profesional', 'adherencia', 'creado']
    list_filter = ['tipo', 'adherencia', 'creado']
    search_fields = ['legajo__codigo', 'descripcion', 'profesional__usuario__username']
    date_hierarchy = 'creado'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('legajo__ciudadano', 'profesional__usuario')


@admin.register(Derivacion)
class DerivacionAdmin(admin.ModelAdmin):
    list_display = ['legajo', 'destino', 'urgencia', 'estado', 'creado']
    list_filter = ['urgencia', 'estado', 'destino__provincia', 'creado']
    search_fields = ['legajo__codigo', 'motivo', 'destino__nombre']
    date_hierarchy = 'creado'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('legajo__ciudadano', 'destino')


@admin.register(EventoCritico)
class EventoCriticoAdmin(admin.ModelAdmin):
    list_display = ['legajo', 'tipo', 'creado']
    list_filter = ['tipo', 'creado']
    search_fields = ['legajo__codigo', 'detalle']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('legajo__ciudadano')


@admin.register(Adjunto)
class AdjuntoAdmin(admin.ModelAdmin):
    list_display = ['etiqueta', 'content_type', 'object_id', 'creado']
    list_filter = ['content_type', 'creado']
    search_fields = ['etiqueta']


@admin.register(AlertaEventoCritico)
class AlertaEventoCriticoAdmin(admin.ModelAdmin):
    list_display = ['evento', 'responsable', 'fecha_cierre']
    list_filter = ['fecha_cierre', 'evento__tipo']
    search_fields = ['evento__legajo__codigo', 'responsable__username']
    readonly_fields = ['fecha_cierre']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('evento__legajo__ciudadano', 'responsable')


# Registrar modelos de contactos en admin
try:
    from .models_contactos import (
        HistorialContacto, VinculoFamiliar, ProfesionalTratante,
        DispositivoVinculado, ContactoEmergencia
    )
    from .admin_contactos import *
except ImportError:
    pass

# Registrar modelos de programas en admin
try:
    from .admin_programas import *
except ImportError:
    pass

# Registrar modelos de Ñachec en admin
try:
    from .admin_nachec import *
except ImportError:
    pass


# ============================================================================
# SISTEMA NODO - MODELOS INSTITUCIONALES
# ============================================================================

@admin.register(InstitucionPrograma)
class InstitucionProgramaAdmin(admin.ModelAdmin):
    list_display = ('institucion', 'programa', 'estado_programa', 'activo', 'cupo_maximo', 'casos_activos_count')
    list_filter = ('estado_programa', 'activo', 'programa')
    search_fields = ('institucion__nombre', 'programa__nombre')
    raw_id_fields = ('institucion', 'responsable_local')
    
    fieldsets = (
        ('Relación', {
            'fields': ('institucion', 'programa')
        }),
        ('Estado', {
            'fields': ('estado_programa', 'activo')
        }),
        ('Control de Cupo', {
            'fields': ('cupo_maximo', 'controlar_cupo', 'permite_sobrecupo')
        }),
        ('Responsable', {
            'fields': ('responsable_local',)
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
    )


@admin.register(DerivacionInstitucional)
class DerivacionInstitucionalAdmin(admin.ModelAdmin):
    list_display = ('ciudadano', 'institucion', 'programa', 'estado', 'urgencia', 'creado')
    list_filter = ('estado', 'urgencia', 'programa', 'creado')
    search_fields = ('ciudadano__dni', 'ciudadano__nombre', 'ciudadano__apellido', 'institucion__nombre')
    raw_id_fields = ('ciudadano', 'derivado_por', 'respondido_por', 'caso_creado')
    readonly_fields = (
        'ciudadano', 'institucion_programa', 'institucion', 'programa', 'motivo', 'urgencia',
        'estado', 'respuesta', 'fecha_respuesta', 'respondido_por', 'caso_creado',
        'derivado_por', 'creado', 'modificado'
    )
    date_hierarchy = 'creado'
    
    fieldsets = (
        ('Derivación', {
            'fields': ('ciudadano', 'institucion_programa', 'motivo', 'urgencia')
        }),
        ('Redundancia (BI)', {
            'fields': ('institucion', 'programa'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('estado', 'respuesta', 'fecha_respuesta', 'respondido_por')
        }),
        ('Caso Creado', {
            'fields': ('caso_creado',)
        }),
        ('Auditoría', {
            'fields': ('derivado_por', 'creado', 'modificado'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DerivacionCiudadano)
class DerivacionCiudadanoAdmin(admin.ModelAdmin):
    list_display = ('ciudadano', 'tipo_inicio', 'institucion', 'programa', 'estado', 'urgencia', 'creado')
    list_filter = ('estado', 'tipo_inicio', 'urgencia', 'programa', 'creado')
    search_fields = ('ciudadano__dni', 'ciudadano__nombre', 'ciudadano__apellido', 'institucion__nombre')
    raw_id_fields = ('ciudadano', 'derivado_por', 'quien_responde', 'caso_creado')
    readonly_fields = ('creado', 'modificado', 'fecha_respuesta')
    date_hierarchy = 'creado'

    fieldsets = (
        ('Derivación', {
            'fields': ('ciudadano', 'tipo_inicio', 'institucion_programa', 'actividad_destino', 'motivo', 'urgencia', 'observaciones')
        }),
        ('Origen', {
            'fields': ('programa_origen',),
            'classes': ('collapse',),
        }),
        ('Redundancia (BI)', {
            'fields': ('institucion', 'programa'),
            'classes': ('collapse',),
        }),
        ('Estado', {
            'fields': ('estado', 'respuesta', 'fecha_respuesta', 'quien_responde')
        }),
        ('Caso Creado', {
            'fields': ('caso_creado',)
        }),
        ('Auditoría', {
            'fields': ('derivado_por', 'creado', 'modificado'),
            'classes': ('collapse',),
        }),
    )


@admin.register(CasoInstitucional)
class CasoInstitucionalAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'ciudadano', 'institucion_programa', 'estado', 'version', 'fecha_apertura')
    list_filter = ('estado', 'institucion_programa__programa', 'fecha_apertura')
    search_fields = ('codigo', 'ciudadano__dni', 'ciudadano__nombre', 'ciudadano__apellido')
    raw_id_fields = ('ciudadano', 'responsable')
    readonly_fields = ('codigo', 'creado', 'modificado', 'dias_activo')
    date_hierarchy = 'fecha_apertura'
    
    fieldsets = (
        ('Identificación', {
            'fields': ('codigo', 'ciudadano', 'institucion_programa', 'version')
        }),
        ('Estado', {
            'fields': ('estado', 'responsable')
        }),
        ('Fechas', {
            'fields': ('fecha_apertura', 'fecha_cierre', 'dias_activo')
        }),
        ('Notas', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('creado', 'modificado'),
            'classes': ('collapse',)
        }),
    )



@admin.register(CoordinadorPrograma)
class CoordinadorProgramaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'programa', 'activo', 'creado')
    list_filter = ('activo', 'programa')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'programa__nombre')
    raw_id_fields = ('usuario',)
    
    fieldsets = (
        ('Asignación', {
            'fields': ('usuario', 'programa', 'activo')
        }),
        ('Auditoría', {
            'fields': ('creado', 'modificado'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario', 'programa')
