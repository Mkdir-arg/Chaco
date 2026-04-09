# Generated manually for performance optimization - MySQL compatible
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX idx_institucion_activo_tipo ON core_institucion(activo, tipo);",
            reverse_sql="DROP INDEX idx_institucion_activo_tipo ON core_institucion;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_institucion_provincia_municipio ON core_institucion(provincia_id, municipio_id);",
            reverse_sql="DROP INDEX idx_institucion_provincia_municipio ON core_institucion;"
        ),
    ]