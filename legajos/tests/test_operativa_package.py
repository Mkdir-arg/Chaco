from django.test import SimpleTestCase

from legajos.views import (
    ActividadesInscritoListView,
    InscribirActividadView,
    actividades_por_institucion,
    marcar_etapa_plan,
)
from legajos.views.operativa import (
    ActividadesInscritoListView as ActividadesInscritoListViewModule,
    InscribirActividadView as InscribirActividadViewModule,
    actividades_por_institucion as actividades_por_institucion_module,
    marcar_etapa_plan as marcar_etapa_plan_module,
)


class LegajosOperativaPackageTests(SimpleTestCase):
    def test_package_expone_views_operativas(self):
        self.assertIs(InscribirActividadView, InscribirActividadViewModule)
        self.assertIs(ActividadesInscritoListView, ActividadesInscritoListViewModule)
        self.assertIs(actividades_por_institucion, actividades_por_institucion_module)
        self.assertIs(marcar_etapa_plan, marcar_etapa_plan_module)
