# Generated migration for unifying Programa models

from django.db import migrations


def migrar_datos(apps, schema_editor):
    """
    No hay datos que migrar porque ProgramaInstitucional nunca existió en la BD.
    Solo existía en el código pero las migraciones anteriores ya usaban Programa.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('legajos', '0018_coordinadorprograma'),
    ]

    operations = [
        migrations.RunPython(migrar_datos, reverse_code=migrations.RunPython.noop),
    ]
