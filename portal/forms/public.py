from django import forms


class ConsultarTramiteForm(forms.Form):
    """DEPRECATED: mantenido solo para compatibilidad de imports."""

    email = forms.EmailField(label="Email", required=False)
