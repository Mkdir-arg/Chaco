from django.test import SimpleTestCase


class TramitesPackageExportsTests(SimpleTestCase):
    def test_views_package_exports_public_functions(self):
        from tramites.views import aprobar_tramite, detalle_tramite, lista_tramites, rechazar_tramite

        self.assertTrue(callable(lista_tramites))
        self.assertTrue(callable(detalle_tramite))
        self.assertTrue(callable(aprobar_tramite))
        self.assertTrue(callable(rechazar_tramite))
