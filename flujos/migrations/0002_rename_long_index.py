from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flujos', '0001_initial'),
    ]

    operations = [
        migrations.RenameIndex(
            model_name='instanciaflujo',
            new_name='ix_instflujo_version_estado',
            old_name='ix_instanciaflujo_version_estado',
        ),
    ]
