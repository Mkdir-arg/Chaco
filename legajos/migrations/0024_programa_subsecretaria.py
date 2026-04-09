import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_secretaria_subsecretaria'),
        ('legajos', '0023_configuracion_turnos_entidades'),
    ]

    operations = [
        migrations.AddField(
            model_name='programa',
            name='subsecretaria',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to='core.subsecretaria',
                verbose_name='Subsecretaría',
            ),
        ),
    ]
