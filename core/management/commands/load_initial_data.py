"""
Carga todos los datos iniciales del sistema para una instalación fresca.

Uso:
    python manage.py load_initial_data

Ejecutar una sola vez al levantar el entorno por primera vez.
Para actualizaciones de grupos en instalaciones existentes, usar:
    python manage.py setup_grupos
"""

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction


USUARIOS_DEMO = [
    # (username, first, last, password, grupos, is_staff)
    ("admin", "Admin", "Sistema", "admin123", [], True),
    ("operador1", "Laura", "Fernández", "demo123", ["ciudadanoVer", "ciudadanoCrear", "conversacionOperar"], True),
    ("configurador1", "Martín", "García", "demo123", ["programaConfigurar", "secretariaConfigurar"], True),
    ("profesional1", "Ana", "Martínez", "demo123", ["ciudadanoVer", "ciudadanoSensible", "Responsable"], True),
    ("encargado1", "Diego", "López", "demo123", ["EncargadoInstitucion"], False),
    ("ciudadano1", "Juan", "Pérez", "demo123", ["Ciudadanos"], False),
]


class Command(BaseCommand):
    help = "Carga datos iniciales para instalación fresca. Solo ejecutar una vez."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== Cargando datos iniciales SistemSo ===\n"))

        # 1. Fixtures de datos de referencia
        self.stdout.write(self.style.MIGRATE_LABEL("Cargando fixtures de referencia..."))
        fixtures = [
            "core/fixtures/dia.json",
            "core/fixtures/mes.json",
            "core/fixtures/sexo.json",
            "core/fixtures/localidad_municipio_provincia.json",
            "legajos/fixtures/contactos_initial_data.json",
        ]
        for fixture in fixtures:
            try:
                call_command("loaddata", fixture, verbosity=0)
                self.stdout.write(self.style.SUCCESS(f"  ✓ {fixture}"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  ⚠ {fixture}: {e}"))

        self.stdout.write("")

        # 2. Grupos del sistema (via comando unificado)
        self.stdout.write(self.style.MIGRATE_LABEL("Configurando grupos del sistema..."))
        call_command("setup_grupos")

        self.stdout.write("")

        # 3. Superusuario
        self.stdout.write(self.style.MIGRATE_LABEL("Creando usuarios demo..."))
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser("superadmin", "superadmin@sistema.gov.ar", "admin123")
            self.stdout.write(self.style.SUCCESS("  ✓ Superusuario: superadmin / admin123"))

        # 4. Usuarios demo
        for username, first, last, pwd, grupos, is_staff in USUARIOS_DEMO:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@sistema.gov.ar",
                    password=pwd,
                    first_name=first,
                    last_name=last,
                    is_staff=is_staff,
                )
                for grupo_nombre in grupos:
                    try:
                        user.groups.add(Group.objects.get(name=grupo_nombre))
                    except Group.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"  ⚠ Grupo no encontrado: {grupo_nombre}"))
                self.stdout.write(self.style.SUCCESS(f"  ✓ {username} ({', '.join(grupos) or 'superadmin'})"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=== Setup completo ==="))
        self.stdout.write("")
        self.stdout.write("Usuarios disponibles:")
        self.stdout.write("  superadmin / admin123  → acceso total")
        self.stdout.write("  admin / admin123       → staff backoffice")
        self.stdout.write("  operador1 / demo123    → operador backoffice")
        self.stdout.write("  configurador1 / demo123 → configurador programas")
        self.stdout.write("  profesional1 / demo123 → profesional / responsable")
        self.stdout.write("  encargado1 / demo123   → encargado institución")
        self.stdout.write("  ciudadano1 / demo123   → portal ciudadano")
