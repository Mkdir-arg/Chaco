from django.contrib import admin
from django.utils.html import format_html
from .models_contactos import (
    HistorialContacto, VinculoFamiliar, ProfesionalTratante,
    DispositivoVinculado, ContactoEmergencia
)


@admin.register(HistorialContacto)
class HistorialContactoAdmin(admin.ModelAdmin):
    list_display = [
        'legajo', 'tipo_contacto', 'fecha_contacto', 'profesional', 
        'estado', 'duracion_formateada', 'seguimiento_requerido'
    ]
    list_filter = [
        'tipo_contacto', 'estado', 'seguimiento_requerido', 
        'fecha_contacto', 'profesional'
    ]
    search_fields = [
        'legajo__ciudadano__nombre', 'legajo__ciudadano__apellido',
        'legajo__codigo', 'motivo', 'resumen'
    ]
    date_hierarchy = 'fecha_contacto'
    ordering = ['-fecha_contacto']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('legajo', 'tipo_contacto', 'fecha_contacto', 'profesional')
        }),
        ('Detalles del Contacto', {
            'fields': ('motivo', 'estado', 'duracion_minutos', 'ubicacion', 'participantes')
        }),
        ('Contenido', {
            'fields': ('resumen', 'acuerdos', 'proximos_pasos')
        }),
        ('Seguimiento', {
            'fields': ('seguimiento_requerido', 'fecha_proximo_contacto', 'archivo_adjunto')
        })
    )


@admin.register(VinculoFamiliar)
class VinculoFamiliarAdmin(admin.ModelAdmin):
    list_display = [
        'ciudadano_principal', 'tipo_vinculo', 'ciudadano_vinculado',
        'es_contacto_emergencia', 'es_referente_tratamiento', 'convive', 'activo'
    ]
    list_filter = [
        'tipo_vinculo', 'es_contacto_emergencia', 'es_referente_tratamiento',
        'convive', 'activo'
    ]
    search_fields = [
        'ciudadano_principal__nombre', 'ciudadano_principal__apellido',
        'ciudadano_vinculado__nombre', 'ciudadano_vinculado__apellido'
    ]
    
    fieldsets = (
        ('Vínculo', {
            'fields': ('ciudadano_principal', 'ciudadano_vinculado', 'tipo_vinculo')
        }),
        ('Características', {
            'fields': ('es_contacto_emergencia', 'es_referente_tratamiento', 'convive')
        }),
        ('Contacto', {
            'fields': ('telefono_alternativo', 'observaciones', 'activo')
        })
    )


@admin.register(ProfesionalTratante)
class ProfesionalTratanteAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 'rol', 'legajo', 'dispositivo', 
        'es_responsable_principal', 'fecha_asignacion', 'activo'
    ]
    list_filter = [
        'rol', 'es_responsable_principal', 'activo', 
        'fecha_asignacion', 'dispositivo'
    ]
    search_fields = [
        'usuario__first_name', 'usuario__last_name', 'usuario__username',
        'legajo__ciudadano__nombre', 'legajo__ciudadano__apellido'
    ]
    date_hierarchy = 'fecha_asignacion'
    
    fieldsets = (
        ('Asignación', {
            'fields': ('legajo', 'usuario', 'rol', 'dispositivo')
        }),
        ('Responsabilidad', {
            'fields': ('es_responsable_principal', 'fecha_asignacion', 'fecha_desasignacion')
        }),
        ('Estado', {
            'fields': ('activo', 'observaciones')
        })
    )


@admin.register(DispositivoVinculado)
class DispositivoVinculadoAdmin(admin.ModelAdmin):
    list_display = [
        'legajo', 'dispositivo', 'fecha_admision', 'fecha_egreso',
        'estado', 'referente_dispositivo'
    ]
    list_filter = ['estado', 'dispositivo', 'fecha_admision']
    search_fields = [
        'legajo__ciudadano__nombre', 'legajo__ciudadano__apellido',
        'dispositivo__nombre'
    ]
    date_hierarchy = 'fecha_admision'
    
    fieldsets = (
        ('Admisión', {
            'fields': ('legajo', 'dispositivo', 'fecha_admision', 'referente_dispositivo')
        }),
        ('Estado', {
            'fields': ('estado', 'fecha_egreso', 'observaciones')
        })
    )


@admin.register(ContactoEmergencia)
class ContactoEmergenciaAdmin(admin.ModelAdmin):
    list_display = [
        'legajo', 'nombre', 'relacion', 'telefono_principal',
        'disponibilidad_24hs', 'prioridad', 'activo'
    ]
    list_filter = ['disponibilidad_24hs', 'prioridad', 'activo']
    search_fields = [
        'nombre', 'relacion', 'telefono_principal',
        'legajo__ciudadano__nombre', 'legajo__ciudadano__apellido'
    ]
    ordering = ['legajo', 'prioridad']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('legajo', 'nombre', 'relacion')
        }),
        ('Contacto', {
            'fields': ('telefono_principal', 'telefono_alternativo', 'email')
        }),
        ('Disponibilidad', {
            'fields': ('disponibilidad_24hs', 'prioridad', 'instrucciones_especiales')
        }),
        ('Estado', {
            'fields': ('activo',)
        })
    )