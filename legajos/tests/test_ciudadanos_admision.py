from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from legajos.forms import AdmisionLegajoForm, CiudadanoConfirmarForm, CiudadanoManualForm
from legajos.models import Ciudadano
from legajos.models_programas import InscripcionPrograma, Programa
from legajos.services import AdmisionSessionService, CiudadanosService


class LegajosCiudadanosAdmisionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="operador-legajos",
            password="clave-segura-123",
            is_staff=True,
        )
        self.ciudadano = Ciudadano.objects.create(
            dni="12345678",
            nombre="Ana",
            apellido="Perez",
            genero=Ciudadano.Genero.FEMENINO,
        )

    def test_ciudadano_forms_define_dni_widget_per_context(self):
        manual_form = CiudadanoManualForm()
        confirm_form = CiudadanoConfirmarForm()

        self.assertNotIn("readonly", manual_form.fields["dni"].widget.attrs)
        self.assertEqual(
            confirm_form.fields["dni"].widget.attrs.get("readonly"),
            True,
        )

    def test_store_and_clear_renaper_data(self):
        session = {}
        resultado = {
            "data": {"dni": "12345678", "nombre": "Ana"},
            "datos_api": {"apellido": "Perez"},
        }

        CiudadanosService.store_renaper_data(session, resultado)

        self.assertEqual(
            CiudadanosService.get_renaper_data(session)["dni"],
            "12345678",
        )
        self.assertEqual(
            CiudadanosService.get_renaper_raw_data(session)["apellido"],
            "Perez",
        )

        CiudadanosService.clear_renaper_data(session)

        self.assertEqual(CiudadanosService.get_renaper_data(session), {})
        self.assertEqual(CiudadanosService.get_renaper_raw_data(session), {})

    def test_create_legajo_from_form_links_pending_inscripcion(self):
        programa = Programa.objects.create(
            codigo="PROG-001",
            nombre="Programa Demo",
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        inscripcion = InscripcionPrograma.objects.create(
            ciudadano=self.ciudadano,
            programa=programa,
            estado=InscripcionPrograma.Estado.PENDIENTE,
        )
        session = {
            AdmisionSessionService.CIUDADANO_SESSION_KEY: self.ciudadano.id,
            AdmisionSessionService.INSCRIPCION_SESSION_KEY: inscripcion.id,
        }
        form = AdmisionLegajoForm(
            data={
                "responsable": "",
                "via_ingreso": "ESPONTANEA",
                "nivel_riesgo": "MEDIO",
                "notas": "Ingreso inicial",
            },
            user=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)

        legajo = AdmisionSessionService.create_legajo_from_form(
            form,
            session,
            self.user,
        )

        inscripcion.refresh_from_db()
        self.assertEqual(str(legajo.id), session["admision_legajo_id"])
        self.assertNotIn("admision_ciudadano_id", session)
        self.assertNotIn("inscripcion_programa_id", session)
        self.assertEqual(inscripcion.legajo_id, legajo.id)
        self.assertEqual(legajo.responsable, self.user)

    def test_admision_paso1_with_preselected_ciudadano_sets_session(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("legajos:admision_paso1"),
            {"ciudadano": self.ciudadano.id},
        )

        self.assertRedirects(response, reverse("legajos:admision_paso2"))
        self.assertEqual(
            self.client.session[AdmisionSessionService.CIUDADANO_SESSION_KEY],
            self.ciudadano.id,
        )

    def test_ciudadano_confirmar_requires_renaper_session(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("legajos:ciudadano_confirmar"))

        self.assertRedirects(response, reverse("legajos:ciudadano_nuevo"))
