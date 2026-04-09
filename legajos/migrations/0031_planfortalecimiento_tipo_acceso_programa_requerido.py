import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legajos', '0030_inscripcionprograma_estado_dado_de_baja'),
    ]

    operations = [
        migrations.AddField(
            model_name='planfortalecimiento',
            name='tipo_acceso',
            field=models.CharField(
                choices=[
                    ('LIBRE', 'Libre (sin requisito)'),
                    ('REQUIERE_PROGRAMA', 'Requiere inscripción a programa'),
                ],
                db_index=True,
                default='LIBRE',
                max_length=20,
                verbose_name='Tipo de acceso',
            ),
        ),
        migrations.AddField(
            model_name='planfortalecimiento',
            name='programa_requerido',
            field=models.ForeignKey(
                blank=True,
                help_text='Solo aplica cuando tipo_acceso = Requiere inscripción a programa',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='actividades_que_requieren',
                to='legajos.programa',
                verbose_name='Programa requerido',
            ),
        ),
    ]
