"""Comando idempotente para garantizar programas base en desarrollo local."""
from django.core.management.base import BaseCommand

from legajos.models_programas import Programa


class Command(BaseCommand):
    help = 'Crea programas de ejemplo para el sistema NODO'

    def handle(self, *args, **options):
        programas_data = [
            {
                'codigo': 'ACOMP-SEDRONAR',
                'nombre': 'Acompañamiento SEDRONAR',
                'tipo': 'ACOMPANAMIENTO_SEDRONAR',
                'descripcion': 'Programa de acompañamiento terapéutico SEDRONAR',
                'icono': 'heart',
                'color': '#EF4444',
                'orden': 1
            },
            {
                'codigo': 'ÑACHEC',
                'nombre': 'ÑACHEC',
                'tipo': 'ÑACHEC',
                'descripcion': 'Programa de ÑACHEC',
                'icono': 'shield-alt',
                'color': '#10B981',
                'orden': 2
            },
            {
                'codigo': 'RED-DANOS',
                'nombre': 'Reducción de Daños',
                'tipo': 'REDUCCION_DANOS',
                'descripcion': 'Programa de reducción de daños y riesgos',
                'icono': 'hand-holding-medical',
                'color': '#F59E0B',
                'orden': 3
            },
            {
                'codigo': 'REINS-SOCIAL',
                'nombre': 'Reinserción Social',
                'tipo': 'REINSERCION_SOCIAL',
                'descripcion': 'Programa de reinserción social y laboral',
                'icono': 'users',
                'color': '#8B5CF6',
                'orden': 4
            },
            {
                'codigo': 'CAPAC-COMUNITARIA',
                'nombre': 'Capacitación Comunitaria',
                'tipo': 'CAPACITACION_COMUNITARIA',
                'descripcion': 'Programa de capacitación a referentes comunitarios',
                'icono': 'graduation-cap',
                'color': '#3B82F6',
                'orden': 5
            },
        ]

        created_count = 0
        updated_count = 0

        for data in programas_data:
            programa, created = Programa.objects.update_or_create(
                tipo=data['tipo'],
                defaults={
                    'codigo': data['codigo'],
                    'nombre': data['nombre'],
                    'descripcion': data['descripcion'],
                    'icono': data['icono'],
                    'color': data['color'],
                    'orden': data['orden'],
                    'estado': Programa.Estado.ACTIVO,
                    'naturaleza': Programa.Naturaleza.PERSISTENTE,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Creado: {programa.nombre}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Actualizado: {programa.nombre}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Proceso completado: {created_count} creados, {updated_count} actualizados'
            )
        )
