from django.test import SimpleTestCase

from turnos import views_backoffice
from turnos.views_configuracion import (
    configuracion_crear,
    configuracion_editar,
    configuracion_lista,
    disponibilidad_agregar,
    disponibilidad_editar,
    disponibilidad_eliminar,
    disponibilidad_grilla,
)
from turnos.views_turnos import (
    agenda,
    api_slots_configuracion,
    backoffice_home,
    bandeja_pendientes,
    turno_aprobar,
    turno_cancelar,
    turno_completar,
    turno_detalle,
    turno_rechazar,
)


class TurnosViewsFachadaTests(SimpleTestCase):
    def test_expone_views_de_configuracion(self):
        self.assertIs(views_backoffice.configuracion_lista, configuracion_lista)
        self.assertIs(views_backoffice.configuracion_crear, configuracion_crear)
        self.assertIs(views_backoffice.configuracion_editar, configuracion_editar)
        self.assertIs(views_backoffice.disponibilidad_grilla, disponibilidad_grilla)
        self.assertIs(views_backoffice.disponibilidad_agregar, disponibilidad_agregar)
        self.assertIs(views_backoffice.disponibilidad_editar, disponibilidad_editar)
        self.assertIs(views_backoffice.disponibilidad_eliminar, disponibilidad_eliminar)

    def test_expone_views_de_turnos(self):
        self.assertIs(views_backoffice.backoffice_home, backoffice_home)
        self.assertIs(views_backoffice.agenda, agenda)
        self.assertIs(views_backoffice.bandeja_pendientes, bandeja_pendientes)
        self.assertIs(views_backoffice.turno_detalle, turno_detalle)
        self.assertIs(views_backoffice.turno_aprobar, turno_aprobar)
        self.assertIs(views_backoffice.turno_rechazar, turno_rechazar)
        self.assertIs(views_backoffice.turno_cancelar, turno_cancelar)
        self.assertIs(views_backoffice.turno_completar, turno_completar)
        self.assertIs(views_backoffice.api_slots_configuracion, api_slots_configuracion)
