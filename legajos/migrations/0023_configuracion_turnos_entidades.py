from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('legajos', '0022_seed_grupo_ciudadanos'),
        ('turnos', '0001_configuracion_turnos'),
    ]

    operations = [
        migrations.AddField(
            model_name='programa',
            name='configuracion_turnos',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='programa',
                to='turnos.configuracionturnos',
                verbose_name='Configuración de turnos',
            ),
        ),
        migrations.AddField(
            model_name='planfortalecimiento',
            name='configuracion_turnos',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='planfortalecimiento',
                to='turnos.configuracionturnos',
                verbose_name='Configuración de turnos',
            ),
        ),
    ]
