"""
Validación del JSON de definición de flujo.
"""
from django import forms


class DefinicionFlujoForm(forms.Form):
    definicion = forms.JSONField(
        label='Definición',
        help_text='JSON con nodos y transiciones del flujo',
    )

    def clean_definicion(self):
        data = self.cleaned_data['definicion']
        if not isinstance(data, dict):
            raise forms.ValidationError('La definición debe ser un objeto JSON.')
        if 'nodos' not in data or not isinstance(data['nodos'], list):
            raise forms.ValidationError('La definición debe incluir una lista "nodos".')
        if 'transiciones' not in data or not isinstance(data['transiciones'], list):
            raise forms.ValidationError('La definición debe incluir una lista "transiciones".')

        tipos_inicio = [n for n in data['nodos'] if n.get('tipo') == 'inicio']
        if len(tipos_inicio) != 1:
            raise forms.ValidationError('El flujo debe tener exactamente un nodo de tipo "inicio".')

        tipos_fin = [n for n in data['nodos'] if n.get('tipo') == 'fin']
        if len(tipos_fin) < 1:
            raise forms.ValidationError('El flujo debe tener al menos un nodo de tipo "fin".')

        return data
