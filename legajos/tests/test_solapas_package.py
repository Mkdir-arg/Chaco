from django.test import SimpleTestCase

from legajos.views import (
    CiudadanoDetalleConSolapasView,
    ciudadano_detalle_con_solapas,
    derivar_a_programa,
)
from legajos.views.solapas import (
    CiudadanoDetalleConSolapasView as CiudadanoDetalleConSolapasViewModule,
    ciudadano_detalle_con_solapas as ciudadano_detalle_con_solapas_module,
    derivar_a_programa as derivar_a_programa_module,
)


class LegajosSolapasPackageTests(SimpleTestCase):
    def test_package_expone_views_de_solapas(self):
        self.assertIs(CiudadanoDetalleConSolapasView, CiudadanoDetalleConSolapasViewModule)
        self.assertIs(ciudadano_detalle_con_solapas, ciudadano_detalle_con_solapas_module)
        self.assertIs(derivar_a_programa, derivar_a_programa_module)
