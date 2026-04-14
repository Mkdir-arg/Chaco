from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0001_turnos_ciudadano'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = []
