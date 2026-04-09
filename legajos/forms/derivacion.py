from django import forms

from ..models_institucional import (
    DerivacionCiudadano,
    InstitucionPrograma,
    TipoInicioDerivacion,
    UrgenciaDerivacion,
)
from ..models_programas import Programa


class DerivarProgramaForm(forms.ModelForm):
    """Formulario para derivar o inscribir directamente a un ciudadano en un programa."""

    class Meta:
        model = DerivacionCiudadano
        fields = ['institucion_programa', 'programa_origen', 'tipo_inicio', 'motivo', 'urgencia', 'observaciones']
        widgets = {
            'institucion_programa': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'programa_origen': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'tipo_inicio': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 4,
                'placeholder': 'Describe el motivo de la derivación...',
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
        allow_inscripcion_directa = kwargs.pop('allow_inscripcion_directa', False)
        super().__init__(*args, **kwargs)

        # Destino: InstitucionPrograma activos
        self.fields['institucion_programa'].queryset = InstitucionPrograma.objects.filter(
            activo=True,
            estado_programa='ACTIVO',
        ).select_related('institucion', 'programa').order_by('programa__orden', 'institucion__nombre')
        self.fields['institucion_programa'].label_from_instance = lambda obj: (
            f"{obj.programa.nombre} — {obj.institucion.nombre}"
        )
        self.fields['institucion_programa'].empty_label = 'Seleccionar programa destino...'

        # Origen: programas activos del ciudadano
        if ciudadano:
            from ..services import SolapasService
            programas_activos = SolapasService.obtener_programas_activos(ciudadano)
            self.fields['programa_origen'].queryset = Programa.objects.filter(
                id__in=[p.programa.id for p in programas_activos]
            )
        else:
            self.fields['programa_origen'].queryset = Programa.objects.none()

        self.fields['programa_origen'].required = False
        self.fields['programa_origen'].empty_label = 'Sin programa origen (espontáneo)'

        # tipo_inicio: solo DERIVACION si el usuario no puede hacer inscripción directa
        if not allow_inscripcion_directa:
            self.fields['tipo_inicio'].widget = forms.HiddenInput()
            self.initial['tipo_inicio'] = TipoInicioDerivacion.DERIVACION
