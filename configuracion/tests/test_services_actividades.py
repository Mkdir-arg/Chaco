from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from core.models import Institucion, Municipio, Provincia, TipoInstitucion
from legajos.models import (
    Ciudadano,
    Derivacion,
    HistorialDerivacion,
    HistorialInscripto,
    HistorialStaff,
    InscriptoActividad,
    LegajoAtencion,
    LegajoInstitucional,
    PersonalInstitucion,
    PlanFortalecimiento,
    StaffActividad,
)

from configuracion.services_actividades import (
    ConfiguracionInstitucionalService,
    ConfiguracionWorkflowError,
)


class ConfiguracionInstitucionalServiceTests(TestCase):
    def setUp(self):
        self.operador = User.objects.create_user(
            username="operador-config",
            password="clave-segura-123",
        )
        self.provincia = Provincia.objects.create(nombre="San Luis")
        self.municipio = Municipio.objects.create(
            nombre="Capital",
            provincia=self.provincia,
        )
        self.institucion = Institucion.objects.create(
            tipo=TipoInstitucion.DTC,
            nombre="Institucion Demo",
            provincia=self.provincia,
            municipio=self.municipio,
            estado_registro="APROBADO",
            activo=True,
        )
        self.legajo_institucional = LegajoInstitucional.objects.create(
            institucion=self.institucion
        )
        self.actividad = PlanFortalecimiento.objects.create(
            legajo_institucional=self.legajo_institucional,
            nombre="Taller Comunitario",
            tipo=PlanFortalecimiento.TipoActividad.PREVENCION,
            subtipo=PlanFortalecimiento.SubtipoActividad.PREVENCION_SELECTIVA,
            descripcion="Actividad institucional",
            cupo_ciudadanos=2,
            fecha_inicio=date.today(),
            estado=PlanFortalecimiento.Estado.ACTIVO,
        )
        self.personal = PersonalInstitucion.objects.create(
            legajo_institucional=self.legajo_institucional,
            nombre="Ana",
            apellido="Gomez",
            dni="30111222",
            tipo=PersonalInstitucion.TipoPersonal.PROFESIONAL,
            activo=True,
        )
        self.ciudadano = Ciudadano.objects.create(
            dni="12345678",
            nombre="Mario",
            apellido="Perez",
            genero=Ciudadano.Genero.MASCULINO,
        )
        self.legajo_atencion = LegajoAtencion.objects.create(
            ciudadano=self.ciudadano,
            dispositivo=self.institucion,
            responsable=self.operador,
        )

    def test_assign_staff_to_actividad_rejects_duplicate_assignment(self):
        StaffActividad.objects.create(
            actividad=self.actividad,
            personal=self.personal,
            rol_en_actividad="Coordinador",
            activo=True,
        )

        with self.assertRaises(ConfiguracionWorkflowError):
            ConfiguracionInstitucionalService.assign_staff_to_actividad(
                self.actividad,
                rol_en_actividad="Coordinador",
                activo=True,
                usuario=self.operador,
                personal=self.personal,
            )

    def test_update_inscripto_estado_finaliza_and_creates_history(self):
        inscripto = InscriptoActividad.objects.create(
            actividad=self.actividad,
            ciudadano=self.ciudadano,
            estado=InscriptoActividad.Estado.ACTIVO,
        )

        changed = ConfiguracionInstitucionalService.update_inscripto_estado(
            inscripto,
            estado=InscriptoActividad.Estado.FINALIZADO,
            observaciones="Cumplio objetivos",
            usuario=self.operador,
        )

        inscripto.refresh_from_db()
        self.assertTrue(changed)
        self.assertEqual(inscripto.estado, InscriptoActividad.Estado.FINALIZADO)
        self.assertEqual(
            HistorialInscripto.objects.filter(
                inscripto=inscripto,
                accion=HistorialInscripto.TipoAccion.FINALIZACION,
            ).count(),
            1,
        )
        self.assertIsNotNone(inscripto.fecha_finalizacion)

    def test_aceptar_derivacion_crea_inscripto_y_historial(self):
        derivacion = Derivacion.objects.create(
            legajo=self.legajo_atencion,
            destino=self.institucion,
            actividad_destino=self.actividad,
            motivo="Seguimiento grupal",
            urgencia=Derivacion.Urgencia.MEDIA,
        )

        derivacion_actualizada, inscripto = (
            ConfiguracionInstitucionalService.aceptar_derivacion(
                derivacion.pk,
                self.operador,
            )
        )

        derivacion_actualizada.refresh_from_db()
        self.assertEqual(derivacion_actualizada.estado, Derivacion.Estado.ACEPTADA)
        self.assertEqual(inscripto.estado, InscriptoActividad.Estado.ACTIVO)
        self.assertTrue(
            HistorialDerivacion.objects.filter(
                derivacion=derivacion,
                accion=HistorialDerivacion.TipoAccion.ACEPTACION,
            ).exists()
        )

    def test_update_staff_registers_history(self):
        staff = StaffActividad.objects.create(
            actividad=self.actividad,
            personal=self.personal,
            rol_en_actividad="Operador",
            activo=True,
        )

        cambios = ConfiguracionInstitucionalService.update_staff(
            staff,
            rol_en_actividad="Coordinador",
            activo=False,
            usuario=self.operador,
        )

        staff.refresh_from_db()
        self.assertEqual(staff.rol_en_actividad, "Coordinador")
        self.assertFalse(staff.activo)
        self.assertTrue(cambios)
        self.assertTrue(
            HistorialStaff.objects.filter(
                staff=staff,
                accion=HistorialStaff.TipoAccion.DESASIGNACION,
            ).exists()
        )
