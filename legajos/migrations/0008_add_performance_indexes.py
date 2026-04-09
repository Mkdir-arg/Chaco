# Generated manually for performance optimization
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('legajos', '0007_empty_migration'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX idx_legajo_ciudadano_dispositivo ON legajos_legajoatencion(ciudadano_id, dispositivo_id);",
            reverse_sql="DROP INDEX idx_legajo_ciudadano_dispositivo ON legajos_legajoatencion;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_legajo_estado_fecha ON legajos_legajoatencion(estado, fecha_apertura);",
            reverse_sql="DROP INDEX idx_legajo_estado_fecha ON legajos_legajoatencion;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_ciudadano_dni_activo ON legajos_ciudadano(dni, activo);",
            reverse_sql="DROP INDEX idx_ciudadano_dni_activo ON legajos_ciudadano;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_seguimiento_legajo_fecha ON legajos_seguimientocontacto(legajo_id, creado);",
            reverse_sql="DROP INDEX idx_seguimiento_legajo_fecha ON legajos_seguimientocontacto;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_derivacion_estado_urgencia ON legajos_derivacion(estado, urgencia);",
            reverse_sql="DROP INDEX idx_derivacion_estado_urgencia ON legajos_derivacion;"
        ),
    ]