from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('legajos', '0028_casoinstitucional_derivacion_origen'),
    ]

    operations = [
        migrations.AddField(
            model_name='derivacionciudadano',
            name='inscripcion_creada',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='derivacion_ciudadano_origen',
                to='legajos.inscripcionprograma',
            ),
        ),
    ]
