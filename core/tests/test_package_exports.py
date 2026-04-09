from django.test import SimpleTestCase


class CorePackageExportsTests(SimpleTestCase):
    def test_views_forms_and_selectors_packages_export_public_symbols(self):
        from core.api_views import InstitucionViewSet, ProvinciaViewSet
        from core.forms import InstitucionForm
        from core.services import ServicioAlertas, ServicioReportes
        from core.selectors import get_localidades_values, get_municipios_values
        from core.signals import get_request_info, invalidate_legajos_cache
        from core.views import (
            dashboard_auditoria,
            inicio_view,
            load_localidad,
            load_municipios,
            performance_dashboard,
        )

        self.assertIsNotNone(InstitucionForm)
        self.assertIsNotNone(ProvinciaViewSet)
        self.assertIsNotNone(InstitucionViewSet)
        self.assertIsNotNone(ServicioAlertas)
        self.assertIsNotNone(ServicioReportes)
        self.assertTrue(callable(get_municipios_values))
        self.assertTrue(callable(get_localidades_values))
        self.assertTrue(callable(dashboard_auditoria))
        self.assertTrue(callable(get_request_info))
        self.assertTrue(callable(inicio_view))
        self.assertTrue(callable(invalidate_legajos_cache))
        self.assertTrue(callable(load_municipios))
        self.assertTrue(callable(load_localidad))
        self.assertTrue(callable(performance_dashboard))
