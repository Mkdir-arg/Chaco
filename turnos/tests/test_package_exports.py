from django.test import SimpleTestCase


class TurnosPackageExportsTests(SimpleTestCase):
    def test_views_package_exports_public_functions(self):
        from turnos.views import agenda, backoffice_home, configuracion_lista, turno_detalle

        self.assertTrue(callable(backoffice_home))
        self.assertTrue(callable(configuracion_lista))
        self.assertTrue(callable(agenda))
        self.assertTrue(callable(turno_detalle))

    def test_services_and_selectors_packages_export_public_symbols(self):
        from turnos.forms import ConfiguracionTurnosForm, DisponibilidadConfiguracionForm
        from turnos.selectors import get_backoffice_home_context
        from turnos.services import (
            TurnoActionError,
            TurnosBackofficeService,
            enviar_email_confirmacion,
        )

        self.assertIsNotNone(ConfiguracionTurnosForm)
        self.assertIsNotNone(DisponibilidadConfiguracionForm)
        self.assertIsNotNone(TurnosBackofficeService)
        self.assertIsNotNone(TurnoActionError)
        self.assertTrue(callable(enviar_email_confirmacion))
        self.assertTrue(callable(get_backoffice_home_context))
