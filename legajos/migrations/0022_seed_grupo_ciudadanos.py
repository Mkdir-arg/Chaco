from django.db import migrations


def crear_grupo_ciudadanos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Ciudadanos')


class Migration(migrations.Migration):

    dependencies = [
        ('legajos', '0021_ciudadano_usuario'),
    ]

    operations = [
        migrations.RunPython(crear_grupo_ciudadanos, migrations.RunPython.noop),
    ]
