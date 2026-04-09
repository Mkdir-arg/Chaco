from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_auditoriaciudadano_ciudadano'),
        ('turnos', '0001_configuracion_turnos'),
    ]

    operations = [
        migrations.AddField(
            model_name='institucion',
            name='configuracion_turnos',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='institucion',
                to='turnos.configuracionturnos',
                verbose_name='Configuración de turnos',
            ),
        ),
    ]
