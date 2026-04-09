import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SolicitudCambioEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nuevo_email', models.EmailField(verbose_name='Nuevo email')),
                ('token', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True, verbose_name='Token de confirmación')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('confirmado', models.BooleanField(default=False)),
                ('expirado', models.BooleanField(default=False)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='solicitudes_cambio_email',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Usuario',
                )),
            ],
            options={
                'verbose_name': 'Solicitud de cambio de email',
                'verbose_name_plural': 'Solicitudes de cambio de email',
            },
        ),
        migrations.AddIndex(
            model_name='solicitudcambioemail',
            index=models.Index(fields=['user', 'confirmado'], name='users_solic_user_id_confirmado_idx'),
        ),
        migrations.AddIndex(
            model_name='solicitudcambioemail',
            index=models.Index(fields=['creado'], name='users_solic_creado_idx'),
        ),
    ]
