from django.test import SimpleTestCase

from legajos.views import (
    alertas_dashboard,
    cursos_actividades_ciudadano,
    derivaciones_programa_api,
    derivar_programa_view,
)
from legajos.views.alertas import alertas_dashboard as alertas_dashboard_module
from legajos.views.api_derivaciones import derivaciones_programa_api as derivaciones_programa_api_module
from legajos.views.cursos import cursos_actividades_ciudadano as cursos_actividades_ciudadano_module
from legajos.views.derivacion import derivar_programa_view as derivar_programa_view_module


class LegajosSupportViewsPackageTests(SimpleTestCase):
    def test_package_expone_views_de_soporte(self):
        self.assertIs(alertas_dashboard, alertas_dashboard_module)
        self.assertIs(cursos_actividades_ciudadano, cursos_actividades_ciudadano_module)
        self.assertIs(derivaciones_programa_api, derivaciones_programa_api_module)
        self.assertIs(derivar_programa_view, derivar_programa_view_module)
