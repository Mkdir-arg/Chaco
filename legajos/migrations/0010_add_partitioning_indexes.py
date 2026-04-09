# Generated manually for performance optimization

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('legajos', '0009_inscriptoactividad_derivacion_actividad_destino_and_more'),
    ]

    operations = [
        # Índices compuestos críticos para tablas de alto volumen
        migrations.RunSQL(
            "CREATE INDEX idx_registro_asistencia_fecha_inscripto ON legajos_registroasistencia (fecha DESC, inscripto_id);",
            reverse_sql="DROP INDEX idx_registro_asistencia_fecha_inscripto ON legajos_registroasistencia;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_historial_actividad_creado_actividad ON legajos_historialactividad (creado DESC, actividad_id);",
            reverse_sql="DROP INDEX idx_historial_actividad_creado_actividad ON legajos_historialactividad;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_historial_inscripto_creado ON legajos_historialinscripto (creado DESC, inscripto_id);",
            reverse_sql="DROP INDEX idx_historial_inscripto_creado ON legajos_historialinscripto;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_alerta_ausentismo_activa_creado ON legajos_alertaausentismo (activa, creado DESC);",
            reverse_sql="DROP INDEX idx_alerta_ausentismo_activa_creado ON legajos_alertaausentismo;"
        ),
    ]