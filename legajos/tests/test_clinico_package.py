from django.test import SimpleTestCase

from legajos.views import LegajoDetailView, LegajoListView, ReportesView
from legajos.views.clinico import (
    LegajoDetailView as LegajoDetailViewModule,
    LegajoListView as LegajoListViewModule,
    ReportesView as ReportesViewModule,
)


class LegajosClinicoPackageTests(SimpleTestCase):
    def test_package_expone_views_clinicas(self):
        self.assertIs(LegajoListView, LegajoListViewModule)
        self.assertIs(LegajoDetailView, LegajoDetailViewModule)
        self.assertIs(ReportesView, ReportesViewModule)
