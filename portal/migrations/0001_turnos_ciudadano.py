# Generated manually — Iteración 6: Sistema de Turnos

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('legajos', '0022_seed_grupo_ciudadanos'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecursoTurnos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre')),
                ('tipo', models.CharField(
                    choices=[
                        ('NODO', 'Institución NODO'),
                        ('ORGANISMO', 'Organismo de Gobierno'),
                        ('PROFESIONAL', 'Profesional'),
                    ],
                    max_length=20,
                    verbose_name='Tipo',
                )),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
                ('direccion', models.CharField(blank=True, max_length=300, verbose_name='Dirección')),
                ('telefono', models.CharField(blank=True, max_length=50, verbose_name='Teléfono')),
                ('email', models.EmailField(blank=True, verbose_name='Email de contacto')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('requiere_aprobacion', models.BooleanField(
                    default=False,
                    help_text='Si está activo, el turno queda pendiente hasta ser confirmado por el backoffice.',
                    verbose_name='Requiere aprobación',
                )),
            ],
            options={
                'verbose_name': 'Recurso de turnos',
                'verbose_name_plural': 'Recursos de turnos',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='DisponibilidadTurnos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recurso', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='disponibilidades',
                    to='portal.recursoturnos',
                    verbose_name='Recurso',
                )),
                ('dia_semana', models.IntegerField(
                    choices=[
                        (0, 'Lunes'),
                        (1, 'Martes'),
                        (2, 'Miércoles'),
                        (3, 'Jueves'),
                        (4, 'Viernes'),
                        (5, 'Sábado'),
                        (6, 'Domingo'),
                    ],
                    verbose_name='Día de la semana',
                )),
                ('hora_inicio', models.TimeField(verbose_name='Hora de inicio')),
                ('hora_fin', models.TimeField(verbose_name='Hora de fin')),
                ('duracion_turno_min', models.PositiveIntegerField(default=30, verbose_name='Duración del turno (minutos)')),
                ('cupo_maximo', models.PositiveIntegerField(default=1, verbose_name='Cupo máximo por slot')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
            ],
            options={
                'verbose_name': 'Disponibilidad de turnos',
                'verbose_name_plural': 'Disponibilidades de turnos',
                'ordering': ['dia_semana', 'hora_inicio'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='disponibilidadturnos',
            unique_together={('recurso', 'dia_semana', 'hora_inicio')},
        ),
        migrations.CreateModel(
            name='TurnoCiudadano',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ciudadano', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='turnos',
                    to='legajos.ciudadano',
                    verbose_name='Ciudadano',
                )),
                ('recurso', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='turnos',
                    to='portal.recursoturnos',
                    verbose_name='Recurso',
                )),
                ('fecha', models.DateField(verbose_name='Fecha')),
                ('hora_inicio', models.TimeField(verbose_name='Hora de inicio')),
                ('hora_fin', models.TimeField(verbose_name='Hora de fin')),
                ('estado', models.CharField(
                    choices=[
                        ('PENDIENTE', 'Pendiente de confirmación'),
                        ('CONFIRMADO', 'Confirmado'),
                        ('CANCELADO_CIU', 'Cancelado por el ciudadano'),
                        ('CANCELADO_SIS', 'Cancelado por el sistema'),
                        ('COMPLETADO', 'Completado'),
                    ],
                    default='PENDIENTE',
                    max_length=20,
                    verbose_name='Estado',
                )),
                ('motivo_consulta', models.TextField(
                    blank=True,
                    help_text='Descripción opcional del motivo del turno.',
                    verbose_name='Motivo de la consulta',
                )),
                ('notas_backoffice', models.TextField(
                    blank=True,
                    help_text='Solo visible para el personal del backoffice.',
                    verbose_name='Notas internas',
                )),
                ('codigo_turno', models.CharField(
                    editable=False,
                    max_length=20,
                    unique=True,
                    verbose_name='Código de turno',
                )),
                ('recordatorio_enviado', models.BooleanField(default=False, verbose_name='Recordatorio enviado')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('modificado', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Turno',
                'verbose_name_plural': 'Turnos',
                'ordering': ['fecha', 'hora_inicio'],
            },
        ),
        migrations.AddIndex(
            model_name='turnociudadano',
            index=models.Index(fields=['ciudadano', 'estado'], name='portal_turn_ciudada_idx'),
        ),
        migrations.AddIndex(
            model_name='turnociudadano',
            index=models.Index(fields=['recurso', 'fecha'], name='portal_turn_recurso_idx'),
        ),
        migrations.AddIndex(
            model_name='turnociudadano',
            index=models.Index(fields=['fecha', 'hora_inicio'], name='portal_turn_fecha_idx'),
        ),
    ]
