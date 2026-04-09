"""
Formularios para gestión programática institucional
"""
from django import forms
from django.core.exceptions import ValidationError

from ..models_institucional import (
    DerivacionCiudadano,
    DerivacionInstitucional,
    CasoInstitucional,
    InstitucionPrograma,
    EstadoDerivacion,
    EstadoCaso,
    UrgenciaDerivacion,
)
from ..models import Ciudadano
from legajos.models_programas import Programa


class DerivacionInstitucionalForm(forms.ModelForm):
    """Formulario para crear derivación institucional programática"""
    
    class Meta:
        model = DerivacionInstitucional
        fields = ['ciudadano', 'institucion_programa', 'motivo', 'urgencia', 'observaciones']
        widgets = {
            'ciudadano': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'institucion_programa': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 4,
                'placeholder': 'Describa el motivo de la derivación...'
            }),
            'urgencia': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 3,
                'placeholder': 'Observaciones adicionales (opcional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        ciudadano = kwargs.pop('ciudadano', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar solo programas activos
        self.fields['institucion_programa'].queryset = InstitucionPrograma.objects.filter(
            activo=True,
            estado_programa='ACTIVO'
        ).select_related('institucion', 'programa').order_by('institucion__nombre', 'programa__orden')
        
        self.fields['institucion_programa'].label_from_instance = lambda obj: (
            f"{obj.institucion.nombre} - {obj.programa.nombre}"
        )
        
        if ciudadano:
            self.fields['ciudadano'].initial = ciudadano
            self.fields['ciudadano'].widget = forms.HiddenInput()


class DerivacionCiudadanoForm(forms.ModelForm):
    """Formulario para crear derivación usando el modelo unificado DerivacionCiudadano."""

    class Meta:
        model = DerivacionCiudadano
        fields = ['ciudadano', 'tipo_inicio', 'institucion_programa', 'programa_origen', 'motivo', 'urgencia', 'observaciones']
        widgets = {
            'ciudadano': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'tipo_inicio': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'institucion_programa': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'programa_origen': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 4,
                'placeholder': 'Describa el motivo de la derivación...',
            }),
            'urgencia': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 3,
                'placeholder': 'Observaciones adicionales (opcional)',
            }),
        }

    def __init__(self, *args, **kwargs):
        ciudadano = kwargs.pop('ciudadano', None)
        super().__init__(*args, **kwargs)

        self.fields['institucion_programa'].queryset = InstitucionPrograma.objects.filter(
            activo=True,
            estado_programa='ACTIVO',
        ).select_related('institucion', 'programa').order_by('institucion__nombre', 'programa__orden')

        self.fields['institucion_programa'].label_from_instance = lambda obj: (
            f"{obj.institucion.nombre} - {obj.programa.nombre}"
        )
        self.fields['programa_origen'].required = False

        if ciudadano:
            self.fields['ciudadano'].initial = ciudadano
            self.fields['ciudadano'].widget = forms.HiddenInput()


class RechazarDerivacionForm(forms.Form):
    """Formulario para rechazar derivación"""
    
    motivo_rechazo = forms.CharField(
        label='Motivo del rechazo',
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 4,
            'placeholder': 'Explique el motivo del rechazo...'
        })
    )


class CambiarEstadoCasoForm(forms.Form):
    """Formulario para cambiar estado de caso"""
    
    nuevo_estado = forms.ChoiceField(
        label='Nuevo estado',
        choices=EstadoCaso.choices,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
        })
    )
    observacion = forms.CharField(
        label='Observación',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 3,
            'placeholder': 'Observaciones sobre el cambio de estado (opcional)'
        })
    )
    motivo_cierre = forms.CharField(
        label='Motivo de cierre',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'rows': 3,
            'placeholder': 'Requerido si el nuevo estado es CERRADO o EGRESADO'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        nuevo_estado = cleaned_data.get('nuevo_estado')
        motivo_cierre = cleaned_data.get('motivo_cierre')
        
        if nuevo_estado in [EstadoCaso.CERRADO, EstadoCaso.EGRESADO] and not motivo_cierre:
            raise ValidationError({
                'motivo_cierre': 'El motivo de cierre es obligatorio para estados CERRADO o EGRESADO'
            })
        
        return cleaned_data


class InstitucionProgramaForm(forms.ModelForm):
    """Formulario para habilitar programa en institución"""
    
    class Meta:
        model = InstitucionPrograma
        fields = [
            'programa', 'estado_programa', 'activo',
            'cupo_maximo', 'controlar_cupo', 'permite_sobrecupo',
            'responsable_local', 'fecha_inicio', 'fecha_fin'
        ]
        widgets = {
            'programa': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'estado_programa': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'cupo_maximo': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'min': '0'
            }),
            'controlar_cupo': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'permite_sobrecupo': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'responsable_local': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'type': 'date'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'type': 'date'
            }),
        }
