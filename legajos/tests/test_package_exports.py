from django.test import SimpleTestCase


class LegajosPackageExportsTests(SimpleTestCase):
    def test_services_and_selectors_packages_export_public_symbols(self):
        from legajos.api_views import CiudadanoViewSet
        from legajos.api_views.contactos import HistorialContactoViewSet
        from legajos.forms import CiudadanoForm, DerivarProgramaForm, DerivacionInstitucionalForm
        from legajos.selectors import build_ciudadano_detail_context
        from legajos.services import (
            AlertasService,
            CasoService,
            CiudadanosService,
            ContactosFilesError,
            DerivacionService,
            FiltrosUsuarioService,
            ServicioOperacionNachec,
            ServicioDeteccionDuplicados,
            ServicioSLA,
            ServicioTransicionNachec,
            SolapasService,
        )

        self.assertIsNotNone(AlertasService)
        self.assertIsNotNone(CasoService)
        self.assertIsNotNone(CiudadanoViewSet)
        self.assertIsNotNone(CiudadanoForm)
        self.assertIsNotNone(CiudadanosService)
        self.assertIsNotNone(DerivarProgramaForm)
        self.assertIsNotNone(DerivacionInstitucionalForm)
        self.assertIsNotNone(DerivacionService)
        self.assertIsNotNone(FiltrosUsuarioService)
        self.assertIsNotNone(HistorialContactoViewSet)
        self.assertIsNotNone(ServicioOperacionNachec)
        self.assertIsNotNone(ServicioDeteccionDuplicados)
        self.assertIsNotNone(ServicioSLA)
        self.assertIsNotNone(ServicioTransicionNachec)
        self.assertIsNotNone(SolapasService)
        self.assertIsNotNone(ContactosFilesError)
        self.assertTrue(callable(build_ciudadano_detail_context))

    def test_legacy_derivacion_form_points_to_unified_model(self):
        from legajos.forms import DerivacionInstitucionalForm

        self.assertIsNotNone(DerivacionInstitucionalForm._meta.model)

    def test_legacy_derivacion_service_is_still_exported(self):
        from legajos.services import DerivacionCiudadanoService, DerivacionService

        self.assertIsNotNone(DerivacionCiudadanoService)
        self.assertIsNotNone(DerivacionService)
