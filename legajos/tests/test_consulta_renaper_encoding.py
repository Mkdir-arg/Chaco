from django.test import SimpleTestCase

from legajos.services.consulta_renaper import reparar_mojibake, reparar_texto_mojibake


class RenaperEncodingTests(SimpleTestCase):
    def test_reparar_texto_mojibake_con_enie(self):
        self.assertEqual(reparar_texto_mojibake("FARIÃA"), "FARIÑA")

    def test_reparar_texto_mojibake_con_acentos(self):
        self.assertEqual(reparar_texto_mojibake("JOSÃ‰ GARCÃA"), "JOSÉ GARCÍA")

    def test_reparar_mojibake_recursivo(self):
        data = {
            "success": True,
            "data": {
                "apellido": "FARIÃA",
                "domicilio": {"calle": "SAN MARTÃN"},
                "observaciones": ["NiÃ±ez", "sin cambios"],
            },
        }

        self.assertEqual(
            reparar_mojibake(data),
            {
                "success": True,
                "data": {
                    "apellido": "FARIÑA",
                    "domicilio": {"calle": "SAN MARTÍN"},
                    "observaciones": ["Niñez", "sin cambios"],
                },
            },
        )
