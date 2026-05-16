from rest_framework import serializers
from .models import (
    Provincia, Municipio, Localidad, Institucion, Sexo, Mes, Dia, Turno
)

# Alias para compatibilidad
DispositivoRed = Institucion


class ProvinciaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Provincia"""
    
    class Meta:
        model = Provincia
        fields = ['id', 'nombre']


class MunicipioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Municipio"""
    provincia = ProvinciaSerializer(read_only=True)
    provincia_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Municipio
        fields = ['id', 'nombre', 'provincia', 'provincia_id']


class LocalidadSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Localidad"""
    municipio = MunicipioSerializer(read_only=True)
    municipio_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Localidad
        fields = ['id', 'nombre', 'municipio', 'municipio_id']


class InstitucionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Institucion"""
    
    class Meta:
        model = Institucion
        fields = ['id', 'nombre']
        read_only_fields = ['id']


# Alias para compatibilidad hacia atrás
DispositivoRedSerializer = InstitucionSerializer


class SexoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Sexo"""
    
    class Meta:
        model = Sexo
        fields = ['id', 'sexo']


class MesSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Mes"""
    
    class Meta:
        model = Mes
        fields = ['id', 'nombre']


class DiaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Dia"""
    
    class Meta:
        model = Dia
        fields = ['id', 'nombre']


class TurnoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Turno"""
    
    class Meta:
        model = Turno
        fields = ['id', 'nombre']