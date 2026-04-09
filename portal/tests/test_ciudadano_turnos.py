from datetime import time, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from legajos.models import Ciudadano
from portal.models import DisponibilidadTurnos, RecursoTurnos, TurnoCiudadano


class CiudadanoTurnosViewsTests(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='Ciudadanos')
        self.user = User.objects.create_user(username='30111222', password='secret')
        self.user.groups.add(self.group)
        self.ciudadano = Ciudadano.objects.create(
            dni='30111222',
            nombre='Ana',
            apellido='Perez',
            genero='F',
            usuario=self.user,
        )
        self.recurso = RecursoTurnos.objects.create(
            nombre='Centro de Atencion',
            tipo=RecursoTurnos.Tipo.ORGANISMO,
            activo=True,
            requiere_aprobacion=False,
        )
        self.fecha = timezone.localdate() + timedelta(days=1)
        DisponibilidadTurnos.objects.create(
            recurso=self.recurso,
            dia_semana=self.fecha.weekday(),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            duracion_turno_min=30,
            cupo_maximo=1,
            activo=True,
        )

    def test_turno_slots_rechaza_fecha_invalida(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('portal:ciudadano_turno_slots', args=[self.recurso.pk]),
            {'fecha': 'fecha-invalida'},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Fecha inválida')

    def test_confirmar_turno_valido_crea_turno(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('portal:ciudadano_confirmar_turno', args=[self.recurso.pk]),
            data={
                'fecha': self.fecha.isoformat(),
                'hora_inicio': '09:00',
                'hora_fin': '09:30',
                'motivo': 'Consulta de seguimiento',
            },
        )

        turno = TurnoCiudadano.objects.get(ciudadano=self.ciudadano)
        self.assertRedirects(
            response,
            reverse('portal:ciudadano_turno_confirmado', args=[turno.pk]),
        )
        self.assertEqual(turno.estado, TurnoCiudadano.Estado.CONFIRMADO)
        self.assertEqual(turno.motivo_consulta, 'Consulta de seguimiento')

    def test_confirmar_turno_sin_cupo_redirige_a_calendario(self):
        TurnoCiudadano.objects.create(
            ciudadano=self.ciudadano,
            recurso=self.recurso,
            fecha=self.fecha,
            hora_inicio=time(9, 0),
            hora_fin=time(9, 30),
            estado=TurnoCiudadano.Estado.CONFIRMADO,
        )
        other_user = User.objects.create_user(username='30999888', password='secret')
        other_user.groups.add(self.group)
        other_ciudadano = Ciudadano.objects.create(
            dni='30999888',
            nombre='Luis',
            apellido='Gomez',
            genero='M',
            usuario=other_user,
        )

        self.client.force_login(other_user)
        response = self.client.post(
            reverse('portal:ciudadano_confirmar_turno', args=[self.recurso.pk]),
            data={
                'fecha': self.fecha.isoformat(),
                'hora_inicio': '09:00',
                'hora_fin': '09:30',
                'motivo': 'Otro motivo valido',
            },
        )

        self.assertRedirects(
            response,
            reverse('portal:ciudadano_turno_calendario', args=[self.recurso.pk]),
        )
        self.assertEqual(TurnoCiudadano.objects.filter(ciudadano=other_ciudadano).count(), 0)
