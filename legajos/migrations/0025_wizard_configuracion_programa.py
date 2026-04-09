from django.db import migrations, models


def convertir_activo_a_estado(apps, schema_editor):
    Programa = apps.get_model('legajos', 'Programa')
    Programa.objects.filter(activo=True).update(estado='ACTIVO')
    Programa.objects.filter(activo=False).update(estado='INACTIVO')


def revertir_estado_a_activo(apps, schema_editor):
    Programa = apps.get_model('legajos', 'Programa')
    Programa.objects.filter(estado='ACTIVO').update(activo=True)
    Programa.objects.exclude(estado='ACTIVO').update(activo=False)


class Migration(migrations.Migration):

    dependencies = [
        ('legajos', '0024_programa_subsecretaria'),
    ]

    operations = [
        # 1. Quitar unique=True y choices de tipo
        migrations.AlterField(
            model_name='programa',
            name='tipo',
            field=models.CharField(blank=True, max_length=50, verbose_name='Tipo'),
        ),
        # 2. Agregar naturaleza (nullable)
        migrations.AddField(
            model_name='programa',
            name='naturaleza',
            field=models.CharField(
                blank=True,
                choices=[('UN_SOLO_ACTO', 'Un solo acto'), ('PERSISTENTE', 'Persistente')],
                max_length=20,
                null=True,
                verbose_name='Naturaleza',
            ),
        ),
        # 3. Agregar estado con default BORRADOR
        migrations.AddField(
            model_name='programa',
            name='estado',
            field=models.CharField(
                choices=[
                    ('BORRADOR', 'Borrador'),
                    ('ACTIVO', 'Activo'),
                    ('SUSPENDIDO', 'Suspendido'),
                    ('INACTIVO', 'Inactivo'),
                ],
                db_index=True,
                default='BORRADOR',
                max_length=20,
                verbose_name='Estado',
            ),
        ),
        # 4. Agregar tiene_turnos
        migrations.AddField(
            model_name='programa',
            name='tiene_turnos',
            field=models.BooleanField(default=False, verbose_name='Tiene turnos'),
        ),
        # 5. Agregar cupo_maximo
        migrations.AddField(
            model_name='programa',
            name='cupo_maximo',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Cupo máximo'),
        ),
        # 6. Agregar tiene_lista_espera
        migrations.AddField(
            model_name='programa',
            name='tiene_lista_espera',
            field=models.BooleanField(default=False, verbose_name='Tiene lista de espera'),
        ),
        # 7. RunPython: convertir activo → estado
        migrations.RunPython(
            convertir_activo_a_estado,
            revertir_estado_a_activo,
        ),
        # 8. Eliminar campo activo
        migrations.RemoveField(
            model_name='programa',
            name='activo',
        ),
        # 9. Índice compuesto estado+orden
        migrations.AddIndex(
            model_name='programa',
            index=models.Index(fields=['estado', 'orden'], name='legajos_pro_estado_orden_idx'),
        ),
    ]
