from django import forms
from ..models import Institucion, Provincia, Municipio, Localidad


class InstitucionForm(forms.ModelForm):
    class Meta:
        model = Institucion
        fields = [
            'tipo', 'nombre', 'provincia', 'municipio', 'localidad',
            'direccion', 'telefono', 'email', 'descripcion',
            'tipo_personeria', 'nro_personeria', 'fecha_personeria', 'cuit',
            'presta_asistencia', 'convenio_obras_sociales', 'nro_sss'
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia': forms.Select(attrs={'class': 'form-select'}),
            'municipio': forms.Select(attrs={'class': 'form-select'}),
            'localidad': forms.Select(attrs={'class': 'form-select'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tipo_personeria': forms.Select(attrs={'class': 'form-select'}),
            'nro_personeria': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_personeria': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cuit': forms.TextInput(attrs={'class': 'form-control'}),
            'nro_sss': forms.TextInput(attrs={'class': 'form-control'}),
        }
