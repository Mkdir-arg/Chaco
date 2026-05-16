from django import forms
from django.contrib.auth.models import User


class CrearUsuarioInstitucionForm(forms.Form):
    username = forms.CharField(label="Usuario", max_length=150)
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    first_name = forms.CharField(label="Nombre", max_length=150)
    last_name = forms.CharField(label="Apellido", max_length=150)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre de usuario ya existe")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("El email ya está registrado")
        return email

class RegistroInstitucionPublicForm(forms.Form):
    """DEPRECATED: registro institucional retirado."""

    nombre = forms.CharField(required=False)


class ConsultarTramiteForm(forms.Form):
    email = forms.EmailField(label="Email")
