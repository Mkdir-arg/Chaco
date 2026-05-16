from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "[DEPRECATED] Comando retirado tras limpieza legacy de dispositivos."

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                "DEPRECATED: verificar_dispositivos fue retirado con la limpieza legacy."
            )
        )
