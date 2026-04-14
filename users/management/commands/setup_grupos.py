"""
Comando unificado para crear todos los grupos Django del sistema.
Idempotente — se puede ejecutar múltiples veces sin efecto secundario.

Uso:
    python manage.py setup_grupos

Incluye:
- Renombrado de grupos legacy (nombres viejos → nombres nuevos acordados)
- Creación de todos los grupos del sistema con nombres definitivos

Ejecutar después de cada deploy o como parte del setup inicial.
"""

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


RENOMBRES_LEGACY = {
    "configurarSecretaria": "secretariaConfigurar",
    "ConfiguracionPrograma": "programaConfigurar",
    "EncargadoDispositivo": "EncargadoInstitucion",
}

GRUPOS = [
    # Ciudadanos
    "ciudadanoVer",
    "ciudadanoCrear",
    "ciudadanoSensible",
    # Instituciones
    "institucionVer",
    "institucionAdministrar",
    # Programas — configuración
    "secretariaConfigurar",
    "programaConfigurar",
    # Programas — operativa
    "programaOperar",
    # Conversaciones
    "conversacionOperar",
    # Dashboard
    "dashboardVer",
    # Configuración sistema
    "sistemaConfigurar",
    # Usuarios y roles
    "usuarioAdministrar",
    # Reportes
    "reportesVer",
    # Roles especiales — portal
    "Ciudadanos",
    # Roles especiales — instituciones (panel institución)
    "EncargadoInstitucion",
    "AdministrativoInstitucion",
    "ProfesorInstitucion",
    # Legacy — profesionales con legajos asignados (SEDRONAR)
    "Responsable",
]


class Command(BaseCommand):
    help = "Crea y/o renombra todos los grupos del sistema. Idempotente."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== Setup de grupos Django ===\n"))

        # 1. Renombrar grupos legacy
        self.stdout.write(self.style.MIGRATE_LABEL("Verificando renombres legacy..."))
        for nombre_viejo, nombre_nuevo in RENOMBRES_LEGACY.items():
            if Group.objects.filter(name=nombre_viejo).exists():
                if not Group.objects.filter(name=nombre_nuevo).exists():
                    Group.objects.filter(name=nombre_viejo).update(name=nombre_nuevo)
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Renombrado: "{nombre_viejo}" → "{nombre_nuevo}"')
                    )
                else:
                    # El nuevo ya existe — eliminar el viejo
                    Group.objects.filter(name=nombre_viejo).delete()
                    self.stdout.write(
                        self.style.WARNING(f'  ~ Eliminado duplicado legacy: "{nombre_viejo}" (ya existe "{nombre_nuevo}")')
                    )
            else:
                self.stdout.write(f'  · "{nombre_viejo}" no existe (OK)')

        self.stdout.write("")

        # 2. Crear grupos faltantes
        self.stdout.write(self.style.MIGRATE_LABEL("Verificando grupos del sistema..."))
        creados = 0
        for nombre in GRUPOS:
            _, created = Group.objects.get_or_create(name=nombre)
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Creado: {nombre}"))
                creados += 1
            else:
                self.stdout.write(f"  · Existe: {nombre}")

        self.stdout.write("")
        if creados:
            self.stdout.write(self.style.SUCCESS(f"Setup completo. {creados} grupo(s) creado(s)."))
        else:
            self.stdout.write(self.style.SUCCESS("Setup completo. Todos los grupos ya existían."))
