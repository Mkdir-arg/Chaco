from django.test import SimpleTestCase

import legajos.views as legajos_views


class LegajosClinicoPackageTests(SimpleTestCase):
    def test_package_no_expone_views_clinicas_retiradas(self):
        self.assertFalse(hasattr(legajos_views, "LegajoListView"))
        self.assertFalse(hasattr(legajos_views, "LegajoDetailView"))
        self.assertFalse(hasattr(legajos_views, "ReportesView"))
