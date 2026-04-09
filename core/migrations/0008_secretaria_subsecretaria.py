import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_institucion_configuracion_turnos'),
    ]

    operations = [
        migrations.CreateModel(
            name='Secretaria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('modificado', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(max_length=200, unique=True, verbose_name='Nombre')),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
                ('activo', models.BooleanField(default=True, verbose_name='Activa')),
            ],
            options={
                'verbose_name': 'Secretaría',
                'verbose_name_plural': 'Secretarías',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Subsecretaria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('modificado', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre')),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
                ('activo', models.BooleanField(default=True, verbose_name='Activa')),
                ('secretaria', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='subsecretarias',
                    to='core.secretaria',
                    verbose_name='Secretaría',
                )),
            ],
            options={
                'verbose_name': 'Subsecretaría',
                'verbose_name_plural': 'Subsecretarías',
                'ordering': ['secretaria__nombre', 'nombre'],
                'unique_together': {('nombre', 'secretaria')},
            },
        ),
    ]
