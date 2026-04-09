from django.test import SimpleTestCase


class LegajosPackageExportsTests(SimpleTestCase):
    def test_services_and_selectors_packages_export_public_symbols(self):
        from legajos.api_views import CiudadanoViewSet
        from legajos.api_views.contactos import HistorialContactoViewSet
        from legajos.forms import CiudadanoForm, DerivarProgramaForm
        from legajos.selectors import (
            build_ciudadano_detail_context,
            get_legajos_report_stats,
        )
        from legajos.services import (
            AdmisionSessionService,
            AlertasService,
            CasoService,
            CiudadanosService,
            ContactosFilesError,
            DerivacionService,
            FiltrosUsuarioService,
            LegajoWorkflowService,
            ServicioOperacionNachec,
            ServicioDeteccionDuplicados,
            ServicioSLA,
            ServicioTransicionNachec,
            SolapasService,
        )

        self.assertIsNotNone(AdmisionSessionService)
        self.assertIsNotNone(AlertasService)
        self.assertIsNotNone(CasoService)
        self.assertIsNotNone(CiudadanoViewSet)
        self.assertIsNotNone(CiudadanoForm)
        self.assertIsNotNone(CiudadanosService)
        self.assertIsNotNone(DerivarProgramaForm)
        self.assertIsNotNone(DerivacionService)
        self.assertIsNotNone(FiltrosUsuarioService)
        self.assertIsNotNone(HistorialContactoViewSet)
        self.assertIsNotNone(LegajoWorkflowService)
        self.assertIsNotNone(ServicioOperacionNachec)
        self.assertIsNotNone(ServicioDeteccionDuplicados)
        self.assertIsNotNone(ServicioSLA)
        self.assertIsNotNone(ServicioTransicionNachec)
        self.assertIsNotNone(SolapasService)
        self.assertIsNotNone(ContactosFilesError)
        self.assertTrue(callable(build_ciudadano_detail_context))
        self.assertTrue(callable(get_legajos_report_stats))
