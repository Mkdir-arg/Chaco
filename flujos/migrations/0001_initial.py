from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('legajos', '0025_wizard_configuracion_programa'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Flujo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('modificado', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre')),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
                ('programa', models.OneToOneField(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='flujo',
                    to='legajos.programa',
                    verbose_name='Programa',
                )),
            ],
            options={
                'verbose_name': 'Flujo',
                'verbose_name_plural': 'Flujos',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='VersionFlujo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_version', models.PositiveIntegerField(db_index=True, verbose_name='Número de versión')),
                ('definicion', models.JSONField(
                    help_text='JSON con nodos y transiciones del flujo',
                    verbose_name='Definición',
                )),
                ('estado', models.CharField(
                    choices=[('BORRADOR', 'Borrador'), ('PUBLICADA', 'Publicada'), ('ARCHIVADA', 'Archivada')],
                    db_index=True,
                    default='BORRADOR',
                    max_length=20,
                    verbose_name='Estado',
                )),
                ('fecha_publicacion', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de publicación')),
                ('flujo', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='versiones',
                    to='flujos.flujo',
                    verbose_name='Flujo',
                )),
                ('creado_por', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='versiones_flujo_creadas',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Creado por',
                )),
            ],
            options={
                'verbose_name': 'Versión de flujo',
                'verbose_name_plural': 'Versiones de flujo',
                'ordering': ['flujo', '-numero_version'],
            },
        ),
        migrations.CreateModel(
            name='InstanciaFlujo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nodo_actual', models.CharField(db_index=True, max_length=255, verbose_name='Nodo actual')),
                ('estado', models.CharField(
                    choices=[('ACTIVA', 'Activa'), ('COMPLETADA', 'Completada'), ('CANCELADA', 'Cancelada')],
                    db_index=True,
                    default='ACTIVA',
                    max_length=20,
                    verbose_name='Estado',
                )),
                ('fecha_inicio', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de inicio')),
                ('fecha_cierre', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de cierre')),
                ('datos', models.JSONField(
                    default=dict,
                    help_text='Datos recopilados durante la ejecución del flujo',
                    verbose_name='Datos acumulados',
                )),
                ('inscripcion', models.OneToOneField(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='instancia_flujo',
                    to='legajos.inscripcionprograma',
                    verbose_name='Inscripción',
                )),
                ('version_flujo', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='instancias',
                    to='flujos.versionflujo',
                    verbose_name='Versión de flujo',
                )),
            ],
            options={
                'verbose_name': 'Instancia de flujo',
                'verbose_name_plural': 'Instancias de flujo',
                'ordering': ['-fecha_inicio'],
            },
        ),
        migrations.CreateModel(
            name='InstanciaLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nodo_desde', models.CharField(blank=True, max_length=255, verbose_name='Nodo origen')),
                ('nodo_hasta', models.CharField(max_length=255, verbose_name='Nodo destino')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Timestamp')),
                ('motivo', models.TextField(blank=True, verbose_name='Motivo')),
                ('datos_transicion', models.JSONField(default=dict, verbose_name='Datos de transición')),
                ('instancia', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='logs',
                    to='flujos.instanciaflujo',
                    verbose_name='Instancia',
                )),
                ('usuario', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='transiciones_flujo',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Usuario',
                )),
            ],
            options={
                'verbose_name': 'Log de instancia',
                'verbose_name_plural': 'Logs de instancia',
                'ordering': ['instancia', 'timestamp'],
            },
        ),
        migrations.AddConstraint(
            model_name='versionflujo',
            constraint=models.UniqueConstraint(
                fields=['flujo', 'numero_version'],
                name='uq_versionflujo_flujo_numero',
            ),
        ),
        migrations.AddIndex(
            model_name='versionflujo',
            index=models.Index(fields=['flujo', 'estado'], name='ix_versionflujo_flujo_estado'),
        ),
        migrations.AddIndex(
            model_name='instanciaflujo',
            index=models.Index(fields=['version_flujo', 'estado'], name='ix_instanciaflujo_version_estado'),
        ),
        migrations.AddIndex(
            model_name='instanciaflujo',
            index=models.Index(fields=['estado', 'nodo_actual'], name='ix_instanciaflujo_estado_nodo'),
        ),
        migrations.AddIndex(
            model_name='instancialog',
            index=models.Index(fields=['instancia', 'timestamp'], name='ix_instancialog_instancia_ts'),
        ),
    ]
