from django.test import SimpleTestCase

from legajos.views.derivacion_programa import (
    aceptar_derivacion_programa,
    rechazar_derivacion_programa,
)


class LegajosDerivacionProgramaPackageTests(SimpleTestCase):
    def test_package_expone_views_de_derivacion_programa(self):
        self.assertTrue(callable(aceptar_derivacion_programa))
        self.assertTrue(callable(rechazar_derivacion_programa))
