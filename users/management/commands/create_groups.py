from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Crea los grupos de usuario básicos"

    def handle(self, *args, **kwargs):
        groups = [
            "Administrador",
            "Ciudadanos",
            "EncargadoDispositivo",
        ]
        self.stdout.write(self.style.SUCCESS("Creando grupos de usuario..."))
        for group_name in groups:
            _group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Grupo "{group_name}" creado'))