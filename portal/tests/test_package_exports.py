from django.test import SimpleTestCase


class PortalPackageExportsTests(SimpleTestCase):
    def test_views_package_exports_public_symbols(self):
        from portal.views import ConsultarTramiteView, PortalHomeView
        from portal.views.ciudadano import ciudadano_mi_perfil

        self.assertIsNotNone(PortalHomeView)
        self.assertIsNotNone(ConsultarTramiteView)
        self.assertTrue(callable(ciudadano_mi_perfil))

    def test_forms_services_and_selectors_packages_export_public_symbols(self):
        from portal.forms import CiudadanoLoginForm, ConsultarTramiteForm
        from portal.selectors import get_ciudadano_perfil, get_portal_home_context
        from portal.services import (
            PortalRegistroService,
            crear_consulta_ciudadana,
            preparar_registro_ciudadano,
        )

        self.assertIsNotNone(CiudadanoLoginForm)
        self.assertIsNotNone(ConsultarTramiteForm)
        self.assertIsNotNone(PortalRegistroService)
        self.assertTrue(callable(get_ciudadano_perfil))
        self.assertTrue(callable(get_portal_home_context))
        self.assertTrue(callable(preparar_registro_ciudadano))
        self.assertTrue(callable(crear_consulta_ciudadana))
