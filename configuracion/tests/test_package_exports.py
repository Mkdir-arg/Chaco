from django.test import SimpleTestCase


class ConfiguracionPackageExportsTests(SimpleTestCase):
    def test_views_package_exports_public_symbols(self):
        from configuracion.views import (
            ActividadDetailView,
            InstitucionDetailView,
            ProvinciaListView,
            StaffEditarView,
        )

        self.assertIsNotNone(ProvinciaListView)
        self.assertIsNotNone(InstitucionDetailView)
        self.assertIsNotNone(ActividadDetailView)
        self.assertIsNotNone(StaffEditarView)

    def test_forms_services_and_selectors_packages_export_public_symbols(self):
        from configuracion.forms import ProvinciaForm
        from configuracion.selectors import (
            build_actividad_detail_context,
            get_instituciones_queryset_for_user,
        )
        from configuracion.services import (
            ConfiguracionInstitucionalService,
            ConfiguracionWorkflowError,
        )

        self.assertIsNotNone(ProvinciaForm)
        self.assertIsNotNone(ConfiguracionInstitucionalService)
        self.assertIsNotNone(ConfiguracionWorkflowError)
        self.assertTrue(callable(build_actividad_detail_context))
        self.assertTrue(callable(get_instituciones_queryset_for_user))
