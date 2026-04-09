from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Ciudadano, LegajoAtencion, EvaluacionInicial, 
    PlanIntervencion, SeguimientoContacto, Derivacion, 
    EventoCritico, Profesional, AlertaCiudadano
)
from core.models import DispositivoRed


class CiudadanoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Ciudadano"""
    legajos_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Ciudadano
        fields = [
            'id', 'dni', 'nombre', 'apellido', 'fecha_nacimiento',
            'genero', 'telefono', 'email', 'domicilio', 'activo',
            'legajos_count', 'creado', 'modificado'
        ]
        read_only_fields = ['id', 'creado', 'modificado']
    
    def get_legajos_count(self, obj):
        return getattr(obj, 'legajos_count', obj.legajos.count())


class DispositivoRedSerializer(serializers.ModelSerializer):
    """Serializer para DispositivoRed"""
    
    class Meta:
        model = DispositivoRed
        fields = ['id', 'nombre', 'tipo', 'activo']


class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para User"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class ProfesionalSerializer(serializers.ModelSerializer):
    """Serializer para Profesional"""
    usuario = UserSerializer(read_only=True)
    
    class Meta:
        model = Profesional
        fields = ['id', 'usuario', 'matricula', 'rol']


class LegajoAtencionSerializer(serializers.ModelSerializer):
    """Serializer para LegajoAtencion"""
    ciudadano = CiudadanoSerializer(read_only=True)
    dispositivo = DispositivoRedSerializer(read_only=True)
    responsable = UserSerializer(read_only=True)
    seguimientos_count = serializers.SerializerMethodField()
    eventos_count = serializers.SerializerMethodField()
    
    class Meta:
        model = LegajoAtencion
        fields = [
            'id', 'codigo', 'ciudadano', 'dispositivo', 'responsable',
            'via_ingreso', 'fecha_admision', 'estado', 'plan_vigente',
            'nivel_riesgo', 'notas', 'fecha_cierre', 'seguimientos_count',
            'eventos_count', 'creado', 'modificado'
        ]
        read_only_fields = ['id', 'codigo', 'creado', 'modificado']
    
    def get_seguimientos_count(self, obj):
        return getattr(obj, 'seguimientos_count', obj.seguimientos.count())
    
    def get_eventos_count(self, obj):
        return getattr(obj, 'eventos_count', obj.eventos.count())


class EvaluacionInicialSerializer(serializers.ModelSerializer):
    """Serializer para EvaluacionInicial"""
    
    class Meta:
        model = EvaluacionInicial
        fields = [
            'id', 'legajo', 'situacion_consumo', 'antecedentes',
            'red_apoyo', 'condicion_social', 'tamizajes',
            'riesgo_suicida', 'violencia', 'creado', 'modificado'
        ]
        read_only_fields = ['id', 'creado', 'modificado']


class PlanIntervencionSerializer(serializers.ModelSerializer):
    """Serializer para PlanIntervencion"""
    profesional = ProfesionalSerializer(read_only=True)
    
    class Meta:
        model = PlanIntervencion
        fields = [
            'id', 'legajo', 'profesional', 'vigente', 'actividades',
            'creado', 'modificado'
        ]
        read_only_fields = ['id', 'creado', 'modificado']


class SeguimientoContactoSerializer(serializers.ModelSerializer):
    """Serializer para SeguimientoContacto"""
    profesional = ProfesionalSerializer(read_only=True)
    
    class Meta:
        model = SeguimientoContacto
        fields = [
            'id', 'legajo', 'profesional', 'tipo', 'descripcion',
            'adherencia', 'adjuntos', 'creado', 'modificado'
        ]
        read_only_fields = ['id', 'creado', 'modificado']


class DerivacionSerializer(serializers.ModelSerializer):
    """Serializer para Derivacion"""
    origen = DispositivoRedSerializer(read_only=True)
    destino = DispositivoRedSerializer(read_only=True)
    
    class Meta:
        model = Derivacion
        fields = [
            'id', 'legajo', 'origen', 'destino', 'motivo', 'urgencia',
            'estado', 'respuesta', 'fecha_aceptacion', 'creado', 'modificado'
        ]
        read_only_fields = ['id', 'creado', 'modificado']


class EventoCriticoSerializer(serializers.ModelSerializer):
    """Serializer para EventoCritico"""
    
    class Meta:
        model = EventoCritico
        fields = [
            'id', 'legajo', 'tipo', 'detalle', 'notificado_a',
            'creado', 'modificado'
        ]
        read_only_fields = ['id', 'creado', 'modificado']


class AlertaCiudadanoSerializer(serializers.ModelSerializer):
    """Serializer para AlertaCiudadano"""
    ciudadano_nombre = serializers.CharField(source='ciudadano.nombre_completo', read_only=True)
    legajo_codigo = serializers.CharField(source='legajo.codigo', read_only=True)
    dispositivo_nombre = serializers.CharField(source='legajo.dispositivo.nombre', read_only=True)
    cerrada_por_nombre = serializers.CharField(source='cerrada_por.get_full_name', read_only=True)
    
    class Meta:
        model = AlertaCiudadano
        fields = [
            'id', 'ciudadano', 'ciudadano_nombre', 'legajo', 'legajo_codigo',
            'dispositivo_nombre', 'tipo', 'prioridad', 'mensaje', 'activa', 
            'fecha_cierre', 'cerrada_por', 'cerrada_por_nombre', 'creado', 'modificado'
        ]
        read_only_fields = ['id', 'creado', 'modificado']


# Importar serializers de contactos
from .serializers_contactos import *