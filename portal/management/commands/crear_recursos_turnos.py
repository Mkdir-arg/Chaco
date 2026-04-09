"""
Comando para crear recursos de turnos y disponibilidades de ejemplo.
Uso: python manage.py crear_recursos_turnos
"""
from datetime import time

from django.core.management.base import BaseCommand

from portal.models import DisponibilidadTurnos, RecursoTurnos


RECURSOS = [
    {
        'nombre': 'NODO Centro',
        'tipo': 'NODO',
        'descripcion': 'Centro de atención social NODO. Atención integral a familias y personas vulnerables.',
        'direccion': 'Av. San Martín 450, Centro',
        'telefono': '(0000) 400-1000',
        'requiere_aprobacion': False,
        'disponibilidades': [
            {'dia_semana': 0, 'hora_inicio': time(8, 0), 'hora_fin': time(12, 0), 'duracion_turno_min': 30, 'cupo_maximo': 2},
            {'dia_semana': 1, 'hora_inicio': time(8, 0), 'hora_fin': time(12, 0), 'duracion_turno_min': 30, 'cupo_maximo': 2},
            {'dia_semana': 2, 'hora_inicio': time(8, 0), 'hora_fin': time(12, 0), 'duracion_turno_min': 30, 'cupo_maximo': 2},
            {'dia_semana': 3, 'hora_inicio': time(14, 0), 'hora_fin': time(17, 0), 'duracion_turno_min': 30, 'cupo_maximo': 2},
            {'dia_semana': 4, 'hora_inicio': time(8, 0), 'hora_fin': time(12, 0), 'duracion_turno_min': 30, 'cupo_maximo': 2},
        ],
    },
    {
        'nombre': 'Secretaría de Desarrollo Social',
        'tipo': 'ORGANISMO',
        'descripcion': 'Atención de trámites y gestiones relacionadas con programas sociales municipales.',
        'direccion': 'Rivadavia 1200, Piso 2, Of. 5',
        'telefono': '(0000) 400-2000',
        'requiere_aprobacion': True,
        'disponibilidades': [
            {'dia_semana': 1, 'hora_inicio': time(9, 0), 'hora_fin': time(13, 0), 'duracion_turno_min': 45, 'cupo_maximo': 1},
            {'dia_semana': 3, 'hora_inicio': time(9, 0), 'hora_fin': time(13, 0), 'duracion_turno_min': 45, 'cupo_maximo': 1},
        ],
    },
    {
        'nombre': 'Lic. María González — Psicóloga',
        'tipo': 'PROFESIONAL',
        'descripcion': 'Atención psicológica individual. Especialista en salud mental comunitaria.',
        'direccion': 'NODO Centro — Av. San Martín 450',
        'telefono': '(0000) 400-3000',
        'requiere_aprobacion': False,
        'disponibilidades': [
            {'dia_semana': 0, 'hora_inicio': time(14, 0), 'hora_fin': time(18, 0), 'duracion_turno_min': 60, 'cupo_maximo': 1},
            {'dia_semana': 2, 'hora_inicio': time(14, 0), 'hora_fin': time(18, 0), 'duracion_turno_min': 60, 'cupo_maximo': 1},
            {'dia_semana': 4, 'hora_inicio': time(9, 0), 'hora_fin': time(13, 0), 'duracion_turno_min': 60, 'cupo_maximo': 1},
        ],
    },
]


class Command(BaseCommand):
    help = 'Crea recursos de turnos y disponibilidades de ejemplo para el portal ciudadano.'

    def handle(self, *args, **options):
        creados = 0
        omitidos = 0

        for datos in RECURSOS:
            disponibilidades = datos['disponibilidades']
            recurso, created = RecursoTurnos.objects.get_or_create(
                nombre=datos['nombre'],
                defaults={
                    'tipo': datos['tipo'],
                    'descripcion': datos['descripcion'],
                    'direccion': datos['direccion'],
                    'telefono': datos['telefono'],
                    'requiere_aprobacion': datos['requiere_aprobacion'],
                },
            )

            if created:
                creados += 1
                self.stdout.write(f'  [+] Creado: {recurso.nombre}')
                for disp_data in disponibilidades:
                    DisponibilidadTurnos.objects.get_or_create(
                        recurso=recurso,
                        dia_semana=disp_data['dia_semana'],
                        hora_inicio=disp_data['hora_inicio'],
                        defaults={
                            'hora_fin': disp_data['hora_fin'],
                            'duracion_turno_min': disp_data['duracion_turno_min'],
                            'cupo_maximo': disp_data['cupo_maximo'],
                        },
                    )
            else:
                omitidos += 1
                self.stdout.write(f'  [=] Ya existe: {recurso.nombre}')

        self.stdout.write(self.style.SUCCESS(
            f'\nListo. Creados: {creados} | Ya existían: {omitidos}'
        ))
