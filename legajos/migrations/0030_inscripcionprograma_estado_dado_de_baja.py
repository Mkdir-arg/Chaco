from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legajos', '0029_derivacionciudadano_inscripcion_creada'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscripcionprograma',
            name='estado',
            field=models.CharField(
                choices=[
                    ('PENDIENTE', 'Pendiente'),
                    ('ACTIVO', 'Activo'),
                    ('EN_SEGUIMIENTO', 'En Seguimiento'),
                    ('SUSPENDIDO', 'Suspendido'),
                    ('CERRADO', 'Cerrado'),
                    ('DADO_DE_BAJA', 'Dado de Baja'),
                ],
                db_index=True,
                default='PENDIENTE',
                max_length=20,
            ),
        ),
    ]
