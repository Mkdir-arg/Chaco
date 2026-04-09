from rest_framework import serializers
from .models import (
    Provincia, Municipio, Localidad, Institucion, DocumentoRequerido, Sexo, Mes, Dia, Turno
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


class DocumentoRequeridoSerializer(serializers.ModelSerializer):
    """Serializer para DocumentoRequerido"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = DocumentoRequerido
        fields = [
            'id', 'tipo', 'tipo_display', 'archivo', 'estado', 'estado_display',
            'observaciones', 'obligatorio', 'creado', 'modificado'
        ]
        read_only_fields = ['id', 'creado', 'modificado']


class InstitucionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Institucion"""
    provincia = ProvinciaSerializer(read_only=True)
    municipio = MunicipioSerializer(read_only=True)
    localidad = LocalidadSerializer(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_registro_display = serializers.CharField(source='get_estado_registro_display', read_only=True)
    tipo_personeria_display = serializers.CharField(source='get_tipo_personeria_display', read_only=True)
    documentos = DocumentoRequeridoSerializer(many=True, read_only=True)
    legajos_count = serializers.SerializerMethodField()
    encargados_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Institucion
        fields = [
            'id', 'tipo', 'tipo_display', 'nombre', 'provincia', 'municipio', 
            'localidad', 'direccion', 'telefono', 'email', 'activo', 'descripcion',
            'estado_registro', 'estado_registro_display', 'fecha_solicitud', 
            'fecha_aprobacion', 'observaciones', 'tipo_personeria', 
            'tipo_personeria_display', 'nro_personeria', 'fecha_personeria', 'cuit',
            'nro_registro', 'resolucion', 'fecha_alta', 'presta_asistencia',
            'convenio_obras_sociales', 'nro_sss', 'documentos', 'legajos_count',
            'encargados_count', 'creado', 'modificado'
        ]
        read_only_fields = ['id', 'fecha_alta', 'creado', 'modificado']
    
    def get_legajos_count(self, obj):
        return getattr(obj, 'legajos_count', obj.legajos.count())
    
    def get_encargados_count(self, obj):
        return getattr(obj, 'encargados_count', obj.encargados.count())


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