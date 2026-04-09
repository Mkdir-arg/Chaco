from django.test import SimpleTestCase


class LegajosSignalsPackageTests(SimpleTestCase):
    def test_signals_package_exports_receivers(self):
        from legajos.signals import (
            alerta_evento_critico,
            crear_caso_nachec_desde_derivacion,
            crear_historial_actividad,
            crear_inscripcion_programa_sedronar,
            invalidate_ciudadano_cache,
        )

        self.assertTrue(callable(alerta_evento_critico))
        self.assertTrue(callable(crear_caso_nachec_desde_derivacion))
        self.assertTrue(callable(crear_historial_actividad))
        self.assertTrue(callable(crear_inscripcion_programa_sedronar))
        self.assertTrue(callable(invalidate_ciudadano_cache))
