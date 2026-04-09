from django.contrib import admin

from .models import Flujo, InstanciaFlujo, InstanciaLog, VersionFlujo


@admin.register(Flujo)
class FlujoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'programa', 'creado')
    search_fields = ('nombre', 'programa__nombre')
    raw_id_fields = ('programa',)


@admin.register(VersionFlujo)
class VersionFlujoAdmin(admin.ModelAdmin):
    list_display = ('flujo', 'numero_version', 'estado', 'fecha_publicacion', 'creado_por')
    list_filter = ('estado',)
    search_fields = ('flujo__nombre',)
    raw_id_fields = ('flujo', 'creado_por')


@admin.register(InstanciaFlujo)
class InstanciaFlujoAdmin(admin.ModelAdmin):
    list_display = ('pk', 'inscripcion', 'version_flujo', 'nodo_actual', 'estado', 'fecha_inicio')
    list_filter = ('estado',)
    raw_id_fields = ('inscripcion', 'version_flujo')


@admin.register(InstanciaLog)
class InstanciaLogAdmin(admin.ModelAdmin):
    list_display = ('pk', 'instancia', 'nodo_desde', 'nodo_hasta', 'timestamp', 'usuario')
    raw_id_fields = ('instancia', 'usuario')
    readonly_fields = ('timestamp',)
