from django.contrib import admin
from .models import ConfiguracionTurnos, DisponibilidadConfiguracion


class DisponibilidadInline(admin.TabularInline):
    model = DisponibilidadConfiguracion
    extra = 0
    fields = ['dia_semana', 'hora_inicio', 'hora_fin', 'duracion_turno_min', 'cupo_maximo', 'activo']


@admin.register(ConfiguracionTurnos)
class ConfiguracionTurnosAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'modo_turno', 'requiere_aprobacion', 'activo', 'creado']
    list_filter = ['activo', 'requiere_aprobacion', 'modo_turno']
    search_fields = ['nombre']
    inlines = [DisponibilidadInline]


@admin.register(DisponibilidadConfiguracion)
class DisponibilidadConfiguracionAdmin(admin.ModelAdmin):
    list_display = ['configuracion', 'dia_semana', 'hora_inicio', 'hora_fin', 'duracion_turno_min', 'cupo_maximo', 'activo']
    list_filter = ['dia_semana', 'activo']
