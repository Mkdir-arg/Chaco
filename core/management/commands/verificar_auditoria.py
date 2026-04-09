from django.core.management.base import BaseCommand
from core.services import ServicioAlertas


class Command(BaseCommand):
    help = 'Ejecuta verificaciones automáticas de auditoría'
    
    def handle(self, *args, **options):
        self.stdout.write('Iniciando verificaciones de auditoría...')
        
        try:
            ServicioAlertas.ejecutar_verificaciones()
            self.stdout.write(
                self.style.SUCCESS('Verificaciones de auditoría completadas exitosamente')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error en verificaciones de auditoría: {e}')
            )
