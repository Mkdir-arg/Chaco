"""Forms para la app de configuracion."""

from django import forms

from core.models import Localidad, Municipio, Provincia

from ..forms_secretaria import SecretariaForm, SubsecretariaForm  # noqa: F401


class ProvinciaForm(forms.ModelForm):
	class Meta:
		model = Provincia
		fields = ["nombre"]


class MunicipioForm(forms.ModelForm):
	class Meta:
		model = Municipio
		fields = ["provincia", "nombre"]


class LocalidadForm(forms.ModelForm):
	class Meta:
		model = Localidad
		fields = ["municipio", "nombre"]
