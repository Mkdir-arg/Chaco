from django.test import SimpleTestCase

from legajos.views import ProgramaDetailView, ProgramaListView
from legajos.views.programas import (
    ProgramaDetailView as ProgramaDetailViewModule,
    ProgramaListView as ProgramaListViewModule,
)


class LegajosProgramasPackageTests(SimpleTestCase):
    def test_package_expone_views_de_programas(self):
        self.assertIs(ProgramaListView, ProgramaListViewModule)
        self.assertIs(ProgramaDetailView, ProgramaDetailViewModule)
