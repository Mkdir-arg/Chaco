from django.test import TestCase
from django.urls import reverse


class RegistroInstitucionViewTests(TestCase):
    def test_institutional_endpoints_are_deprecated(self):
        response_crear = self.client.get(reverse("portal:crear_usuario"))
        response_registro = self.client.get(reverse("portal:registro_institucion"))
        response_consulta = self.client.get(reverse("portal:consultar_tramite"))

        self.assertEqual(response_crear.status_code, 410)
        self.assertEqual(response_registro.status_code, 410)
        self.assertEqual(response_consulta.status_code, 410)
