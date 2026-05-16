from django import forms


class DerivarProgramaForm(forms.Form):
    """DEPRECATED: formulario legacy de SEDRONAR retirado."""

    def __init__(self, *args, **kwargs):
        kwargs.pop('ciudadano', None)
        kwargs.pop('allow_inscripcion_directa', None)
        super().__init__(*args, **kwargs)
        self.add_error(
            None,
            'DEPRECATED: DerivarProgramaForm fue deshabilitado tras la eliminación de models_institucional.',
        )

    def save(self, commit=True):  # pragma: no cover
        raise NotImplementedError(
            'DEPRECATED: DerivarProgramaForm no tiene persistencia activa.'
        )
