from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0001_turnos_ciudadano'),
        ('turnos', '0001_configuracion_turnos'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Vínculo de RecursoTurnos a ConfiguracionTurnos
        migrations.AddField(
            model_name='recursoturnos',
            name='configuracion_turnos',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='recursoturnos',
                to='turnos.configuracionturnos',
                verbose_name='Configuración de turnos',
            ),
        ),
        # TurnoCiudadano: hacer recurso nullable (era NOT NULL)
        migrations.AlterField(
            model_name='turnociudadano',
            name='recurso',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='turnos',
                to='portal.recursoturnos',
                verbose_name='Recurso (legacy)',
            ),
        ),
        # TurnoCiudadano: campos nuevos
        migrations.AddField(
            model_name='turnociudadano',
            name='configuracion',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='turnos',
                to='turnos.configuracionturnos',
                verbose_name='Configuración de turnos',
            ),
        ),
        migrations.AddField(
            model_name='turnociudadano',
            name='contexto_tipo',
            field=models.CharField(
                choices=[
                    ('PROGRAMA', 'Programa social'),
                    ('INSTITUCION', 'Institución'),
                    ('ACTIVIDAD', 'Actividad institucional'),
                    ('GENERICO', 'Genérico'),
                ],
                default='GENERICO',
                max_length=20,
                verbose_name='Tipo de contexto',
            ),
        ),
        migrations.AddField(
            model_name='turnociudadano',
            name='contexto_id',
            field=models.PositiveIntegerField(
                blank=True, null=True, verbose_name='ID de la entidad origen'
            ),
        ),
        migrations.AddField(
            model_name='turnociudadano',
            name='aprobado_por',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='turnos_aprobados',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Aprobado por',
            ),
        ),
        migrations.AddField(
            model_name='turnociudadano',
            name='fecha_aprobacion',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de aprobación'),
        ),
        migrations.AddField(
            model_name='turnociudadano',
            name='email_confirmacion_enviado',
            field=models.BooleanField(default=False, verbose_name='Email de confirmación enviado'),
        ),
        migrations.AddField(
            model_name='turnociudadano',
            name='email_cancelacion_enviado',
            field=models.BooleanField(default=False, verbose_name='Email de cancelación enviado'),
        ),
        # Índices nuevos
        migrations.AddIndex(
            model_name='turnociudadano',
            index=models.Index(fields=['configuracion', 'fecha'], name='portal_turn_conf_fecha_idx'),
        ),
        migrations.AddIndex(
            model_name='turnociudadano',
            index=models.Index(fields=['configuracion', 'estado'], name='portal_turn_conf_estado_idx'),
        ),
    ]
