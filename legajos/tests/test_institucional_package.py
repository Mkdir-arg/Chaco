from django.test import SimpleTestCase

from legajos.views import (
    api_programa_indicadores,
    institucion_detalle_programatico,
    programa_derivaciones,
)
from legajos.views.institucional import (
    api_programa_indicadores as api_programa_indicadores_module,
    institucion_detalle_programatico as institucion_detalle_programatico_module,
    programa_derivaciones as programa_derivaciones_module,
)


class LegajosInstitucionalPackageTests(SimpleTestCase):
    def test_package_expone_views_institucionales(self):
        self.assertIs(institucion_detalle_programatico, institucion_detalle_programatico_module)
        self.assertIs(programa_derivaciones, programa_derivaciones_module)
        self.assertIs(api_programa_indicadores, api_programa_indicadores_module)
