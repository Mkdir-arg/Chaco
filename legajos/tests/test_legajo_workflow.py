from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import Institucion, Localidad, Municipio, Provincia
from legajos.forms import EvaluacionInicialForm, EventoCriticoForm, PlanIntervencionForm, SeguimientoForm
from legajos.models import Ciudadano, Derivacion, LegajoAtencion, SeguimientoContacto
from legajos.selectors import get_legajos_report_stats, get_seguimientos_dashboard_metrics
from legajos.services import LegajoWorkflowService


class LegajoWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='profesional-legajo',
            password='clave-segura-123',
            is_staff=True,
        )
        self.other_user = User.objects.create_user(
            username='responsable-nuevo',
            password='clave-segura-123',
            is_staff=True,
        )
        self.provincia = Provincia.objects.create(nombre='Chaco')
        self.municipio = Municipio.objects.create(
            nombre='Resistencia',
            provincia=self.provincia,
        )
        self.localidad = Localidad.objects.create(
            nombre='Centro',
            municipio=self.municipio,
        )
        self.dispositivo = Institucion.objects.create(
            tipo='DTC',
            nombre='Dispositivo Central',
            provincia=self.provincia,
            municipio=self.municipio,
            localidad=self.localidad,
            direccion='Calle 123',
            activo=True,
        )
        self.destino = Institucion.objects.create(
            tipo='CAAC',
            nombre='Institucion Destino',
            provincia=self.provincia,
            municipio=self.municipio,
            localidad=self.localidad,
            direccion='Avenida 456',
            activo=True,
        )
        self.ciudadano = Ciudadano.objects.create(
            dni='30111222',
            nombre='Lucia',
            apellido='Gomez',
            genero=Ciudadano.Genero.FEMENINO,
        )
        self.legajo = LegajoAtencion.objects.create(
            ciudadano=self.ciudadano,
            dispositivo=self.dispositivo,
            responsable=self.user,
            via_ingreso=LegajoAtencion.ViaIngreso.ESPONTANEA,
            nivel_riesgo=LegajoAtencion.NivelRiesgo.MEDIO,
        )

    def test_save_evaluacion_from_form_persists_tamizajes(self):
        form = EvaluacionInicialForm(
            data={
                'situacion_consumo': 'Consumo problemático reciente',
                'antecedentes': 'Sin internaciones previas',
                'red_apoyo': 'Familia ampliada',
                'condicion_social': 'Trabajo informal',
                'riesgo_suicida': 'on',
                'violencia': '',
                'assist_puntaje': 12,
                'phq9_puntaje': 7,
            },
        )

        self.assertTrue(form.is_valid(), form.errors)

        evaluacion = LegajoWorkflowService.save_evaluacion_from_form(form, self.legajo)

        self.assertEqual(evaluacion.legajo, self.legajo)
        self.assertEqual(evaluacion.tamizajes['ASSIST']['puntaje'], 12)
        self.assertEqual(evaluacion.tamizajes['PHQ9']['puntaje'], 7)
        self.assertTrue(evaluacion.riesgo_suicida)

    def test_save_plan_from_form_preserves_dynamic_activity_slots(self):
        form = PlanIntervencionForm(
            data={
                'vigente': 'on',
                'actividad_1': 'Entrevista individual',
                'frecuencia_1': 'Semanal',
                'responsable_1': 'Operador',
                'actividad_4': 'Taller grupal',
                'frecuencia_4': 'Quincenal',
                'responsable_4': 'Equipo territorial',
            }
        )

        self.assertTrue(form.is_valid(), form.errors)

        plan = LegajoWorkflowService.save_plan_from_form(form, self.legajo, self.user)

        self.assertEqual(plan.legajo, self.legajo)
        self.assertEqual(plan.profesional.usuario, self.user)
        self.assertEqual(len(plan.actividades), 2)
        self.assertEqual(plan.actividades[1]['accion'], 'Taller grupal')
        self.assertTrue(plan.vigente)

    def test_save_seguimiento_from_form_assigns_profesional(self):
        form = SeguimientoForm(
            data={
                'tipo': SeguimientoContacto.TipoContacto.ENTREVISTA,
                'descripcion': 'Se realizó entrevista de seguimiento.',
                'adherencia': SeguimientoContacto.Adherencia.ADECUADA,
            }
        )

        self.assertTrue(form.is_valid(), form.errors)

        seguimiento = LegajoWorkflowService.save_seguimiento_from_form(
            form,
            self.legajo,
            self.user,
        )

        self.assertEqual(seguimiento.legajo, self.legajo)
        self.assertEqual(seguimiento.profesional.usuario, self.user)
        self.assertEqual(seguimiento.tipo, SeguimientoContacto.TipoContacto.ENTREVISTA)

    def test_seguimientos_dashboard_metrics_counts_each_type(self):
        profesional = LegajoWorkflowService.get_or_create_profesional(self.user)
        SeguimientoContacto.objects.create(
            legajo=self.legajo,
            profesional=profesional,
            tipo=SeguimientoContacto.TipoContacto.ENTREVISTA,
            descripcion='Entrevista 1',
        )
        SeguimientoContacto.objects.create(
            legajo=self.legajo,
            profesional=profesional,
            tipo=SeguimientoContacto.TipoContacto.VISITA,
            descripcion='Visita 1',
        )
        SeguimientoContacto.objects.create(
            legajo=self.legajo,
            profesional=profesional,
            tipo=SeguimientoContacto.TipoContacto.LLAMADA,
            descripcion='Llamada 1',
        )

        metrics = get_seguimientos_dashboard_metrics(self.legajo)

        self.assertEqual(metrics['total_seguimientos'], 3)
        self.assertEqual(metrics['entrevistas_count'], 1)
        self.assertEqual(metrics['visitas_count'], 1)
        self.assertEqual(metrics['llamadas_count'], 1)

    def test_save_evento_from_form_maps_notificados(self):
        form = EventoCriticoForm(
            data={
                'tipo': 'CRISIS',
                'detalle': 'Se registró una crisis aguda.',
                'notificar_familia': 'on',
                'notificar_autoridades': '',
                'notificar_otros': 'Equipo territorial',
            }
        )

        self.assertTrue(form.is_valid(), form.errors)

        evento = LegajoWorkflowService.save_evento_from_form(form, self.legajo)

        self.assertEqual(evento.legajo, self.legajo)
        self.assertEqual(evento.notificado_a, ['Familia', 'Equipo territorial'])

    def test_change_legajo_responsable_updates_notes(self):
        legajo = LegajoWorkflowService.change_legajo_responsable(
            self.legajo,
            self.other_user,
            self.user,
        )

        self.assertEqual(legajo.responsable, self.other_user)
        self.assertIn('Responsable cambiado de', legajo.notas)
        self.assertIn(self.other_user.username, legajo.notas)

    def test_change_legajo_responsable_rejects_unauthorized_user(self):
        actor = User.objects.create_user(
            username='sin-permisos',
            password='clave-segura-123',
            is_staff=True,
        )

        with self.assertRaises(ValidationError):
            LegajoWorkflowService.change_legajo_responsable(
                self.legajo,
                self.other_user,
                actor,
            )

    def test_get_legajos_report_stats_returns_quality_metrics(self):
        profesional = LegajoWorkflowService.get_or_create_profesional(self.user)
        SeguimientoContacto.objects.create(
            legajo=self.legajo,
            profesional=profesional,
            tipo=SeguimientoContacto.TipoContacto.ENTREVISTA,
            descripcion='Seguimiento para métricas',
            adherencia=SeguimientoContacto.Adherencia.ADECUADA,
        )
        Derivacion.objects.create(
            legajo=self.legajo,
            destino=self.destino,
            motivo='Articulación con otro dispositivo',
            urgencia=Derivacion.Urgencia.MEDIA,
            estado=Derivacion.Estado.ACEPTADA,
        )
        evento_form = EventoCriticoForm(
            data={
                'tipo': 'CRISIS',
                'detalle': 'Evento para reporte',
            }
        )
        self.assertTrue(evento_form.is_valid(), evento_form.errors)
        LegajoWorkflowService.save_evento_from_form(evento_form, self.legajo)

        stats = get_legajos_report_stats()

        self.assertEqual(stats['total_legajos'], 1)
        self.assertEqual(stats['legajos_activos'], 1)
        self.assertGreaterEqual(stats['metricas_calidad']['adherencia_adecuada'], 100.0)
        self.assertEqual(stats['metricas_calidad']['tasa_derivacion'], 100.0)
        self.assertGreater(stats['metricas_calidad']['eventos_por_100'], 0)

    def test_legajo_reabrir_view_reopens_closed_legajo(self):
        self.client.force_login(self.user)
        self.legajo.estado = LegajoAtencion.Estado.CERRADO
        self.legajo.fecha_cierre = timezone.localdate() - timedelta(days=2)
        self.legajo.save(update_fields=['estado', 'fecha_cierre'])

        response = self.client.post(
            reverse('legajos:reabrir', kwargs={'pk': self.legajo.pk}),
            {'motivo_reapertura': 'Retoma tratamiento'},
        )

        self.assertRedirects(
            response,
            reverse('legajos:detalle', kwargs={'pk': self.legajo.pk}),
        )
        self.legajo.refresh_from_db()
        self.assertEqual(self.legajo.estado, LegajoAtencion.Estado.EN_SEGUIMIENTO)
        self.assertIsNone(self.legajo.fecha_cierre)
