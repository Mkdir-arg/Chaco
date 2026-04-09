from django.core.management.base import BaseCommand
from django.db import transaction
from legajos.models import LegajoAtencion
from legajos.models_programas import Programa, InscripcionPrograma


class Command(BaseCommand):
    help = 'Migra legajos existentes al sistema de programas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la migración sin guardar cambios',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Modo DRY RUN - No se guardarán cambios'))
        
        try:
            programa_sedronar = Programa.objects.get(tipo='ACOMPANAMIENTO_SEDRONAR')
        except Programa.DoesNotExist:
            self.stdout.write(self.style.ERROR('Error: Programa SEDRONAR no encontrado'))
            self.stdout.write('Ejecuta: python manage.py loaddata programas_initial')
            return
        
        legajos = LegajoAtencion.objects.select_related('ciudadano', 'responsable').all()
        total = legajos.count()
        creados = 0
        existentes = 0
        
        self.stdout.write(f'Procesando {total} legajos...')
        
        with transaction.atomic():
            for legajo in legajos:
                # Verificar si ya existe inscripción
                existe = InscripcionPrograma.objects.filter(
                    ciudadano=legajo.ciudadano,
                    programa=programa_sedronar
                ).exists()
                
                if existe:
                    existentes += 1
                    continue
                
                # Mapear estado del legajo al estado de inscripción
                estado_map = {
                    'ABIERTO': 'ACTIVO',
                    'EN_SEGUIMIENTO': 'EN_SEGUIMIENTO',
                    'CERRADO': 'CERRADO',
                }
                estado = estado_map.get(legajo.estado, 'ACTIVO')
                
                if not dry_run:
                    InscripcionPrograma.objects.create(
                        ciudadano=legajo.ciudadano,
                        programa=programa_sedronar,
                        via_ingreso='DIRECTO',
                        estado=estado,
                        responsable=legajo.responsable,
                        legajo_id=legajo.id,
                        fecha_inscripcion=legajo.fecha_apertura,
                        fecha_inicio=legajo.fecha_apertura,
                        fecha_cierre=legajo.fecha_cierre,
                        notas=f'Migrado desde LegajoAtencion {legajo.codigo}'
                    )
                
                creados += 1
                
                if creados % 100 == 0:
                    self.stdout.write(f'Procesados: {creados}/{total}')
            
            if dry_run:
                raise Exception('DRY RUN - Revertir transacción')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Migración completada'))
        self.stdout.write(f'  - Total legajos: {total}')
        self.stdout.write(f'  - Inscripciones creadas: {creados}')
        self.stdout.write(f'  - Ya existentes: {existentes}')
