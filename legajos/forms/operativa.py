from django import forms

from ..models import InscriptoActividad, PlanFortalecimiento


class InscribirActividadForm(forms.ModelForm):
    """Formulario para inscribir ciudadano a actividad del centro"""

    class Meta:
        model = InscriptoActividad
        fields = ['actividad', 'observaciones']
        widgets = {
            'actividad': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                }
            ),
            'observaciones': forms.Textarea(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                    'rows': 3,
                    'placeholder': 'Observaciones sobre la inscripción (opcional)',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        legajo = kwargs.pop('legajo', None)
        super().__init__(*args, **kwargs)

        if legajo:
            self.fields['actividad'].queryset = PlanFortalecimiento.objects.filter(
                legajo_institucional__institucion=legajo.dispositivo,
                estado='ACTIVO',
            ).select_related('legajo_institucional__institucion')
            self.fields['actividad'].label_from_instance = (
                lambda obj: f"{obj.nombre} ({obj.get_tipo_display()})"
            )
        else:
            self.fields['actividad'].queryset = PlanFortalecimiento.objects.none()
