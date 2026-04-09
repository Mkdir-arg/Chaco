from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('legajos', '0027_data_copiar_derivaciones'),
    ]

    operations = [
        migrations.AddField(
            model_name='casoinstitucional',
            name='derivacion_origen',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='caso_originado',
                to='legajos.derivacionciudadano',
                verbose_name='Derivación de origen',
            ),
        ),
    ]
