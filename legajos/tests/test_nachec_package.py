from django.test import SimpleTestCase

from legajos.views import completar_validacion, dashboard_nachec, iniciar_prestacion
from legajos.views.nachec_dashboard import dashboard_nachec as dashboard_nachec_module
from legajos.views.nachec_operacion import completar_validacion as completar_validacion_module
from legajos.views.nachec_prestaciones import iniciar_prestacion as iniciar_prestacion_module


class LegajosNachecPackageTests(SimpleTestCase):
    def test_package_expone_views_nachec(self):
        self.assertIs(dashboard_nachec, dashboard_nachec_module)
        self.assertIs(completar_validacion, completar_validacion_module)
        self.assertIs(iniciar_prestacion, iniciar_prestacion_module)
