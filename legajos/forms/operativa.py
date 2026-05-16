from django import forms


class InscribirActividadForm(forms.Form):
    """DEPRECATED: formulario retirado con limpieza legacy."""

    actividad = forms.CharField(required=False)
    observaciones = forms.CharField(required=False, widget=forms.Textarea)
