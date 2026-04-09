from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('legajos', '0025_wizard_configuracion_programa'),
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── Paso 1: renombrar related_names legacy en DerivacionInstitucional ──
        migrations.AlterField(
            model_name='derivacioninstitucional',
            name='ciudadano',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='derivaciones_institucionales_legacy',
                to='legajos.ciudadano',
            ),
        ),
        migrations.AlterField(
            model_name='derivacioninstitucional',
            name='institucion',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='derivaciones_recibidas_legacy',
                to='core.institucion',
            ),
        ),
        migrations.AlterField(
            model_name='derivacioninstitucional',
            name='programa',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='derivaciones_programa_legacy',
                to='legajos.programa',
            ),
        ),
        migrations.AlterField(
            model_name='derivacioninstitucional',
            name='institucion_programa',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='derivaciones_legacy',
                to='legajos.institucionprograma',
            ),
        ),
        migrations.AlterField(
            model_name='derivacioninstitucional',
            name='derivado_por',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='derivaciones_institucionales_realizadas_legacy',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='derivacioninstitucional',
            name='respondido_por',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='derivaciones_institucionales_respondidas_legacy',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='derivacioninstitucional',
            name='caso_creado',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='derivacion_creadora_legacy',
                to='legajos.casoinstitucional',
            ),
        ),
        # ── Paso 2: crear el nuevo modelo ──
        migrations.CreateModel(
            name='DerivacionCiudadano',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('modificado', models.DateTimeField(auto_now=True)),
                ('tipo_inicio', models.CharField(
                    choices=[('DERIVACION', 'Derivación'), ('INSCRIPCION_DIRECTA', 'Inscripción Directa')],
                    default='DERIVACION',
                    max_length=25,
                )),
                ('estado', models.CharField(
                    choices=[('PENDIENTE', 'Pendiente'), ('ACEPTADA', 'Aceptada'), ('RECHAZADA', 'Rechazada')],
                    db_index=True,
                    default='PENDIENTE',
                    max_length=20,
                )),
                ('urgencia', models.CharField(
                    choices=[('BAJA', 'Baja'), ('MEDIA', 'Media'), ('ALTA', 'Alta')],
                    db_index=True,
                    default='MEDIA',
                    max_length=10,
                )),
                ('motivo', models.TextField()),
                ('observaciones', models.TextField(blank=True)),
                ('respuesta', models.TextField(blank=True)),
                ('fecha_respuesta', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('ciudadano', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='derivaciones_ciudadanos',
                    to='legajos.ciudadano',
                )),
                ('institucion_programa', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='derivaciones',
                    to='legajos.institucionprograma',
                )),
                ('actividad_destino', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='derivaciones_ciudadanos',
                    to='legajos.planfortalecimiento',
                )),
                ('programa_origen', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='derivaciones_originadas',
                    to='legajos.programa',
                )),
                ('institucion', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='derivaciones_ciudadanos_recibidas',
                    to='core.institucion',
                )),
                ('programa', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='derivaciones_ciudadanos',
                    to='legajos.programa',
                )),
                ('derivado_por', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='derivaciones_ciudadanos_realizadas',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('quien_responde', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='derivaciones_ciudadanos_respondidas',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('caso_creado', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='derivacion_ciudadano_creadora',
                    to='legajos.casoinstitucional',
                )),
            ],
            options={
                'verbose_name': 'Derivación Ciudadano',
                'verbose_name_plural': 'Derivaciones Ciudadano',
                'ordering': ['-creado'],
            },
        ),
        migrations.AddIndex(
            model_name='derivacionciudadano',
            index=models.Index(fields=['ciudadano', 'estado'], name='der_ciu_estado_idx'),
        ),
        migrations.AddIndex(
            model_name='derivacionciudadano',
            index=models.Index(fields=['institucion_programa', 'estado'], name='der_ip_estado_idx'),
        ),
        migrations.AddIndex(
            model_name='derivacionciudadano',
            index=models.Index(fields=['estado', 'urgencia'], name='der_estado_urgencia_idx'),
        ),
        migrations.AddIndex(
            model_name='derivacionciudadano',
            index=models.Index(fields=['institucion', 'programa'], name='der_inst_prog_idx'),
        ),
    ]
