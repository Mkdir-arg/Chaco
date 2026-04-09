import secrets
import string

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def generar_codigos_existentes(apps, schema_editor):
    """Asigna código de inscripción a todos los registros existentes."""
    InscriptoActividad = apps.get_model('legajos', 'InscriptoActividad')
    alphabet = string.ascii_uppercase + string.digits
    codigos_usados = set()

    for inscripto in InscriptoActividad.objects.all():
        for _ in range(20):
            codigo = ''.join(secrets.choice(alphabet) for _ in range(8))
            if codigo not in codigos_usados:
                codigos_usados.add(codigo)
                inscripto.codigo_inscripcion = codigo
                inscripto.save(update_fields=['codigo_inscripcion'])
                break
        else:
            raise RuntimeError(
                f'No se pudo generar código único para InscriptoActividad pk={inscripto.pk}'
            )


class Migration(migrations.Migration):

    dependencies = [
        ('legajos', '0031_planfortalecimiento_tipo_acceso_programa_requerido'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1. Agregar campos nuevos (ambos opcionales inicialmente)
        migrations.AddField(
            model_name='inscriptoactividad',
            name='codigo_inscripcion',
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=8,
                verbose_name='Código de inscripción',
                default='',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inscriptoactividad',
            name='inscrito_por',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='inscripciones_realizadas',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Inscripto por',
            ),
        ),
        # 2. Poblar códigos en registros existentes
        migrations.RunPython(
            generar_codigos_existentes,
            reverse_code=migrations.RunPython.noop,
        ),
        # 3. Aplicar UNIQUE en codigo_inscripcion
        migrations.AlterField(
            model_name='inscriptoactividad',
            name='codigo_inscripcion',
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=8,
                unique=True,
                verbose_name='Código de inscripción',
            ),
        ),
        # 4. Eliminar unique_together legacy
        migrations.AlterUniqueTogether(
            name='inscriptoactividad',
            unique_together=set(),
        ),
    ]
