from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from core.models import Institucion, Municipio, Provincia, TipoInstitucion


class RegistroInstitucionViewTests(TestCase):
    def setUp(self):
        self.provincia = Provincia.objects.create(nombre="San Luis")
        self.municipio = Municipio.objects.create(
            nombre="Capital", provincia=self.provincia
        )

    def test_crear_usuario_institucion_creates_inactive_user_and_pending_session(self):
        response = self.client.post(
            reverse("portal:crear_usuario"),
            data={
                "username": "institucion-demo",
                "email": "encargado@example.com",
                "password": "clave-segura-123",
                "first_name": "Maria",
                "last_name": "Lopez",
            },
        )

        self.assertRedirects(response, reverse("portal:registro_institucion"))
        user = User.objects.get(username="institucion-demo")
        self.assertFalse(user.is_active)
        self.assertTrue(user.groups.filter(name="EncargadoInstitucion").exists())
        self.assertEqual(self.client.session["pending_user_id"], user.id)

    def test_registro_institucion_assigns_pending_user(self):
        user = User.objects.create_user(
            username="institucion-demo",
            email="encargado@example.com",
            password="clave-segura-123",
            is_active=False,
        )
        Group.objects.get_or_create(name="EncargadoInstitucion")
        user.groups.add(Group.objects.get(name="EncargadoInstitucion"))
        session = self.client.session
        session["pending_user_id"] = user.id
        session.save()

        response = self.client.post(
            reverse("portal:registro_institucion"),
            data={
                "tipo": TipoInstitucion.DTC,
                "nombre": "Institucion Test",
                "provincia": str(self.provincia.pk),
                "municipio": str(self.municipio.pk),
                "localidad": "",
                "direccion": "Calle 123",
                "telefono": "2664123456",
                "email": "contacto@institucion.org",
                "descripcion": "Descripcion",
                "tipo_personeria": "",
                "nro_personeria": "",
                "fecha_personeria": "",
                "cuit": "",
                "presta_asistencia": "on",
                "convenio_obras_sociales": "",
                "nro_sss": "",
            },
        )

        self.assertRedirects(response, reverse("portal:consultar_tramite"))
        institucion = Institucion.objects.get(nombre="Institucion Test")
        self.assertEqual(institucion.estado_registro, "ENVIADO")
        self.assertTrue(institucion.encargados.filter(pk=user.pk).exists())
        self.assertNotIn("pending_user_id", self.client.session)
