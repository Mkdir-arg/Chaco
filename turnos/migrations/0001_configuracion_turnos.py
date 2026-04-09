from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ConfiguracionTurnos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('requiere_aprobacion', models.BooleanField(default=False, help_text='Si está activo, el turno queda pendiente hasta ser confirmado por el backoffice.', verbose_name='Requiere aprobación')),
                ('modo_turno', models.CharField(choices=[('AUTO', 'Automático (ciudadano elige slot)'), ('MANUAL', 'Manual (operador asigna)'), ('AMBOS', 'Ambos')], default='AUTO', max_length=10, verbose_name='Modo de asignación')),
                ('anticipacion_minima_hs', models.PositiveIntegerField(default=24, help_text='Horas mínimas de anticipación para reservar un turno.', verbose_name='Anticipación mínima (horas)')),
                ('anticipacion_maxima_dias', models.PositiveIntegerField(default=30, help_text='Hasta cuántos días en el futuro puede reservarse un turno.', verbose_name='Anticipación máxima (días)')),
                ('permite_cancelacion_ciudadano', models.BooleanField(default=True, verbose_name='Permite cancelación por ciudadano')),
                ('cancelacion_hasta_hs', models.PositiveIntegerField(default=24, help_text='El ciudadano puede cancelar hasta X horas antes del turno.', verbose_name='Cancelación hasta (horas antes)')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('modificado', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Configuración de turnos',
                'verbose_name_plural': 'Configuraciones de turnos',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='DisponibilidadConfiguracion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia_semana', models.IntegerField(choices=[(0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')], verbose_name='Día de la semana')),
                ('hora_inicio', models.TimeField(verbose_name='Hora de inicio')),
                ('hora_fin', models.TimeField(verbose_name='Hora de fin')),
                ('duracion_turno_min', models.PositiveIntegerField(default=30, verbose_name='Duración del turno (minutos)')),
                ('cupo_maximo', models.PositiveIntegerField(default=1, verbose_name='Cupo máximo por slot')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('configuracion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='disponibilidades', to='turnos.configuracionturnos', verbose_name='Configuración')),
            ],
            options={
                'verbose_name': 'Disponibilidad',
                'verbose_name_plural': 'Disponibilidades',
                'ordering': ['dia_semana', 'hora_inicio'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='disponibilidadconfiguracion',
            unique_together={('configuracion', 'dia_semana', 'hora_inicio')},
        ),
    ]
