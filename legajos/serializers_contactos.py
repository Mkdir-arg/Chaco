from rest_framework import serializers
from django.contrib.auth.models import User
from .models_contactos import (
    HistorialContacto, VinculoFamiliar, ProfesionalTratante,
    DispositivoVinculado, ContactoEmergencia
)
from .models import Ciudadano, LegajoAtencion
from core.models import DispositivoRed


class CiudadanoBasicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ciudadano
        fields = ['id', 'dni', 'nombre', 'apellido', 'telefono']


class HistorialContactoSerializer(serializers.ModelSerializer):
    profesional_nombre = serializers.CharField(source='profesional.get_full_name', read_only=True)
    ciudadano_nombre = serializers.CharField(source='legajo.ciudadano.__str__', read_only=True)
    duracion_formateada = serializers.CharField(read_only=True)
    
    class Meta:
        model = HistorialContacto
        fields = '__all__'
        read_only_fields = ('creado', 'modificado')
    
    def validate_fecha_contacto(self, value):
        from datetime import datetime
        if value > datetime.now():
            raise serializers.ValidationError("La fecha de contacto no puede ser futura")
        return value


class VinculoFamiliarSerializer(serializers.ModelSerializer):
    ciudadano_principal_nombre = serializers.CharField(source='ciudadano_principal.__str__', read_only=True)
    ciudadano_vinculado_nombre = serializers.CharField(source='ciudadano_vinculado.__str__', read_only=True)
    ciudadano_vinculado_detail = CiudadanoBasicoSerializer(source='ciudadano_vinculado', read_only=True)
    tipo_vinculo_display = serializers.CharField(source='get_tipo_vinculo_display', read_only=True)
    
    class Meta:
        model = VinculoFamiliar
        fields = '__all__'
        read_only_fields = ('creado', 'modificado')
    
    def validate(self, data):
        if data['ciudadano_principal'] == data['ciudadano_vinculado']:
            raise serializers.ValidationError("Un ciudadano no puede vincularse consigo mismo")
        return data


class ProfesionalTratanteSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    dispositivo_nombre = serializers.CharField(source='dispositivo.nombre', read_only=True)
    legajo_codigo = serializers.CharField(source='legajo.codigo', read_only=True)
    
    class Meta:
        model = ProfesionalTratante
        fields = '__all__'
        read_only_fields = ('creado', 'modificado', 'fecha_asignacion')


class DispositivoVinculadoSerializer(serializers.ModelSerializer):
    dispositivo_nombre = serializers.CharField(source='dispositivo.nombre', read_only=True)
    referente_nombre = serializers.CharField(source='referente_dispositivo.get_full_name', read_only=True)
    
    class Meta:
        model = DispositivoVinculado
        fields = '__all__'
        read_only_fields = ('creado', 'modificado')


class ContactoEmergenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactoEmergencia
        fields = '__all__'
        read_only_fields = ('creado', 'modificado')
    
    def validate_prioridad(self, value):
        if value < 1:
            raise serializers.ValidationError("La prioridad debe ser mayor a 0")
        return value


# Serializers para listados y búsquedas
class HistorialContactoListSerializer(serializers.ModelSerializer):
    profesional_nombre = serializers.CharField(source='profesional.get_full_name', read_only=True)
    tipo_contacto_display = serializers.CharField(source='get_tipo_contacto_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = HistorialContacto
        fields = [
            'id', 'fecha_contacto', 'tipo_contacto', 'tipo_contacto_display',
            'estado', 'estado_display', 'motivo', 'profesional_nombre',
            'duracion_minutos', 'seguimiento_requerido'
        ]


class UserBasicoSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'nombre_completo']