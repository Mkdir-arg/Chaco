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
