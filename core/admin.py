from django.contrib import admin

from core.models import (
    Localidad,
    Provincia,
    Municipio,
    Sexo,
    Mes,
    Dia,
    Turno,
    Institucion,
    DocumentoRequerido,
)
from core.models_auditoria import LogAccion, LogDescargaArchivo, SesionUsuario, AlertaAuditoria
from core.models_auditoria_extendida import (
    AuditoriaCiudadano, AuditoriaLegajo, AuditoriaEvaluacion,
    AuditoriaEventoCritico, AuditoriaConsentimiento, AuditoriaAccesoSensible,
    AuditoriaDerivacion, AuditoriaPlanIntervencion, AuditoriaInstitucion, OperacionMasiva
)

admin.site.register(Provincia)
admin.site.register(Municipio)
admin.site.register(Sexo)
admin.site.register(Mes)
admin.site.register(Dia)
admin.site.register(Turno)


@admin.register(Localidad)
class LocalidadAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('municipio__provincia')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "municipio":
            provincia_id = request.GET.get("provincia")
            if provincia_id:
                kwargs["queryset"] = Municipio.objects.filter(provincia_id=provincia_id).select_related('provincia')
            else:
                kwargs["queryset"] = Municipio.objects.select_related('provincia')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class DocumentoRequeridoInline(admin.TabularInline):
    model = DocumentoRequerido
    extra = 0
    fields = ('tipo', 'archivo', 'estado', 'obligatorio', 'observaciones')
    readonly_fields = ('creado',)


@admin.register(Institucion)
class InstitucionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "estado_registro", "activo", "municipio", "provincia")
    list_filter = ("tipo", "estado_registro", "activo", "provincia", "presta_asistencia")
    search_fields = ("nombre", "municipio__nombre", "provincia__nombre", "nro_registro")
    ordering = ("provincia", "municipio", "nombre")
    inlines = [DocumentoRequeridoInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('provincia', 'municipio', 'localidad').prefetch_related('encargados', 'documentos')
    
    fieldsets = (
        ("Información Básica", {
            "fields": ("nombre", "tipo", "activo", "descripcion")
        }),
        ("Ubicación", {
            "fields": ("provincia", "municipio", "localidad", "direccion")
        }),
        ("Contacto", {
            "fields": ("telefono", "email")
        }),
        ("Estado del Registro", {
            "fields": ("estado_registro", "fecha_solicitud", "fecha_aprobacion", "observaciones")
        }),
        ("Información Legal", {
            "fields": ("tipo_personeria", "nro_personeria", "fecha_personeria", "cuit")
        }),
        ("Registro SEDRONAR", {
            "fields": ("nro_registro", "resolucion", "fecha_alta")
        }),
        ("Servicios", {
            "fields": ("presta_asistencia", "convenio_obras_sociales", "nro_sss")
        }),
        ("Personal", {
            "fields": ("encargados",)
        }),
    )
    
    filter_horizontal = ('encargados',)
    
    def get_readonly_fields(self, request, obj=None):
        readonly = ['fecha_alta']
        if obj and obj.estado_registro == 'APROBADO':
            readonly.extend(['nro_registro', 'resolucion', 'fecha_aprobacion'])
        return readonly


@admin.register(DocumentoRequerido)
class DocumentoRequeridoAdmin(admin.ModelAdmin):
    list_display = ('institucion', 'tipo', 'estado', 'obligatorio', 'creado')
    list_filter = ('tipo', 'estado', 'obligatorio')
    search_fields = ('institucion__nombre',)
    ordering = ('institucion', 'tipo')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('institucion')


# Alias para compatibilidad hacia atrás
DispositivoRedAdmin = InstitucionAdmin


# Modelos de Auditoría
@admin.register(LogAccion)
class LogAccionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'accion', 'modelo', 'objeto_repr', 'timestamp', 'ip_address')
    list_filter = ('accion', 'modelo', 'timestamp')
    search_fields = ('usuario__username', 'modelo', 'objeto_repr')
    readonly_fields = ('usuario', 'accion', 'modelo', 'objeto_id', 'objeto_repr', 'detalles', 'ip_address', 'user_agent', 'timestamp')
    ordering = ('-timestamp',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(LogDescargaArchivo)
class LogDescargaArchivoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'archivo_nombre', 'timestamp', 'ip_address')
    list_filter = ('timestamp',)
    search_fields = ('usuario__username', 'archivo_nombre')
    readonly_fields = ('usuario', 'archivo_nombre', 'archivo_path', 'modelo_origen', 'objeto_id', 'ip_address', 'user_agent', 'timestamp')
    ordering = ('-timestamp',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SesionUsuario)
class SesionUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'inicio_sesion', 'ultima_actividad', 'activa', 'ip_address')
    list_filter = ('activa', 'inicio_sesion')
    search_fields = ('usuario__username',)
    readonly_fields = ('usuario', 'session_key', 'ip_address', 'user_agent', 'inicio_sesion', 'ultima_actividad', 'fin_sesion')
    ordering = ('-inicio_sesion',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')
    
    def has_add_permission(self, request):
        return False


@admin.register(AlertaAuditoria)
class AlertaAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'severidad', 'usuario_afectado', 'timestamp', 'revisada')
    list_filter = ('tipo', 'severidad', 'revisada', 'timestamp')
    search_fields = ('usuario_afectado__username', 'descripcion')
    readonly_fields = ('tipo', 'severidad', 'usuario_afectado', 'descripcion', 'detalles', 'timestamp')
    ordering = ('-timestamp',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario_afectado', 'revisada_por')
    
    def has_add_permission(self, request):
        return False



# Nuevos Modelos de Auditoría Extendida
@admin.register(AuditoriaCiudadano)
class AuditoriaCiudadanoAdmin(admin.ModelAdmin):
    list_display = ('ciudadano', 'accion', 'usuario', 'timestamp', 'modifico_datos_personales')
    list_filter = ('accion', 'modifico_datos_personales', 'timestamp')
    search_fields = ('ciudadano__dni', 'ciudadano__nombre', 'usuario__username')
    readonly_fields = ('ciudadano', 'accion', 'usuario', 'campos_modificados', 'datos_anteriores', 'datos_nuevos', 'ip_address', 'user_agent', 'timestamp', 'motivo', 'modifico_datos_personales')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AuditoriaLegajo)
class AuditoriaLegajoAdmin(admin.ModelAdmin):
    list_display = ('legajo', 'accion', 'usuario', 'timestamp', 'cambio_estado', 'cambio_responsable')
    list_filter = ('accion', 'cambio_estado', 'cambio_responsable', 'cambio_nivel_riesgo', 'timestamp')
    search_fields = ('legajo__codigo', 'usuario__username')
    readonly_fields = ('legajo', 'accion', 'usuario', 'campo_modificado', 'valor_anterior', 'valor_nuevo', 'datos_completos_anteriores', 'datos_completos_nuevos', 'ip_address', 'timestamp', 'motivo')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AuditoriaEvaluacion)
class AuditoriaEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('evaluacion', 'accion', 'usuario', 'timestamp', 'genera_alerta', 'cambio_riesgo_suicida')
    list_filter = ('accion', 'genera_alerta', 'cambio_riesgo_suicida', 'cambio_violencia', 'timestamp')
    search_fields = ('evaluacion__legajo__codigo', 'usuario__username')
    readonly_fields = ('evaluacion', 'accion', 'usuario', 'campos_modificados', 'datos_anteriores', 'datos_nuevos', 'timestamp', 'ip_address', 'genera_alerta')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AuditoriaEventoCritico)
class AuditoriaEventoCriticoAdmin(admin.ModelAdmin):
    list_display = ('evento', 'tipo_evento', 'accion', 'usuario', 'timestamp')
    list_filter = ('accion', 'tipo_evento', 'timestamp')
    search_fields = ('evento__legajo__codigo', 'usuario__username')
    readonly_fields = ('evento', 'accion', 'usuario', 'datos_anteriores', 'datos_nuevos', 'timestamp', 'ip_address', 'notificados', 'tipo_evento')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AuditoriaConsentimiento)
class AuditoriaConsentimientoAdmin(admin.ModelAdmin):
    list_display = ('consentimiento', 'accion', 'usuario', 'timestamp', 'archivo_nombre')
    list_filter = ('accion', 'timestamp')
    search_fields = ('consentimiento__ciudadano__dni', 'usuario__username')
    readonly_fields = ('consentimiento', 'accion', 'usuario', 'datos_completos', 'timestamp', 'ip_address', 'archivo_hash', 'archivo_nombre', 'motivo', 'aprobado_por')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AuditoriaAccesoSensible)
class AuditoriaAccesoSensibleAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'object_id', 'usuario', 'tipo_acceso', 'timestamp', 'fuera_horario', 'acceso_multiple')
    list_filter = ('tipo_acceso', 'fuera_horario', 'acceso_multiple', 'timestamp')
    search_fields = ('usuario__username', 'object_id')
    readonly_fields = ('content_type', 'object_id', 'usuario', 'tipo_acceso', 'campos_accedidos', 'ip_address', 'user_agent', 'timestamp', 'justificacion', 'url_acceso', 'metodo_http')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AuditoriaDerivacion)
class AuditoriaDerivacionAdmin(admin.ModelAdmin):
    list_display = ('derivacion', 'accion', 'usuario', 'estado_nuevo', 'timestamp', 'cambio_estado')
    list_filter = ('accion', 'cambio_estado', 'cambio_urgencia', 'timestamp')
    search_fields = ('derivacion__legajo__codigo', 'usuario__username')
    readonly_fields = ('derivacion', 'accion', 'usuario', 'estado_anterior', 'estado_nuevo', 'datos_completos', 'timestamp', 'ip_address', 'institucion_origen', 'institucion_destino')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AuditoriaPlanIntervencion)
class AuditoriaPlanIntervencionAdmin(admin.ModelAdmin):
    list_display = ('plan', 'accion', 'usuario', 'timestamp', 'cambio_vigencia')
    list_filter = ('accion', 'cambio_vigencia', 'timestamp')
    search_fields = ('plan__legajo__codigo', 'usuario__username')
    readonly_fields = ('plan', 'accion', 'usuario', 'campos_modificados', 'datos_anteriores', 'datos_nuevos', 'timestamp', 'ip_address', 'cambio_vigencia')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AuditoriaInstitucion)
class AuditoriaInstitucionAdmin(admin.ModelAdmin):
    list_display = ('institucion', 'accion', 'usuario', 'timestamp', 'cambio_estado_registro', 'cambio_activo')
    list_filter = ('accion', 'cambio_estado_registro', 'cambio_activo', 'timestamp')
    search_fields = ('institucion__nombre', 'usuario__username')
    readonly_fields = ('institucion', 'accion', 'usuario', 'campos_modificados', 'datos_anteriores', 'datos_nuevos', 'timestamp', 'ip_address', 'cambio_estado_registro', 'estado_registro_anterior', 'estado_registro_nuevo')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(OperacionMasiva)
class OperacionMasivaAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'modelo_afectado', 'usuario', 'cantidad_registros', 'registros_exitosos', 'completada', 'fecha_inicio')
    list_filter = ('tipo', 'completada', 'fecha_inicio')
    search_fields = ('usuario__username', 'modelo_afectado')
    readonly_fields = ('tipo', 'usuario', 'modelo_afectado', 'cantidad_registros', 'registros_exitosos', 'registros_fallidos', 'archivo_origen', 'archivo_log', 'fecha_inicio', 'fecha_fin', 'completada', 'errores', 'ip_address')
    ordering = ('-fecha_inicio',)
    date_hierarchy = 'fecha_inicio'
    
    def has_add_permission(self, request):
        return False
