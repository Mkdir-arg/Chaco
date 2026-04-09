from django import forms

from legajos.models import ClaseActividad


class ClaseActividadForm(forms.ModelForm):
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        label='Fecha',
    )
    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
        label='Hora de inicio',
    )

    class Meta:
        model = ClaseActividad
        fields = ['fecha', 'hora_inicio', 'duracion_minutos', 'titulo']
        widgets = {
            'duracion_minutos': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'placeholder': 'Ej: 90'}),
            'titulo': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Opcional'}),
        }
        labels = {
            'duracion_minutos': 'Duración (minutos)',
            'titulo': 'Título',
        }

    def clean(self):
        cleaned_data = super().clean()
        actividad = self.instance.actividad if self.instance.pk else getattr(self, '_actividad', None)
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')

        if actividad and fecha and fecha < actividad.fecha_inicio:
            self.add_error('fecha', f'La fecha no puede ser anterior al inicio de la actividad ({actividad.fecha_inicio}).')

        return cleaned_data
