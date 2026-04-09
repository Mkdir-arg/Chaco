import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from core.models import Provincia


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dark_mode = models.BooleanField(default=True)
    es_usuario_provincial = models.BooleanField(default=False)
    provincia = models.ForeignKey(
        Provincia, on_delete=models.SET_NULL, null=True, blank=True
    )
    rol = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"


class SolicitudCambioEmail(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes_cambio_email',
        verbose_name='Usuario',
    )
    nuevo_email = models.EmailField(verbose_name='Nuevo email')
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        db_index=True,
        editable=False,
        verbose_name='Token de confirmación',
    )
    creado = models.DateTimeField(auto_now_add=True)
    confirmado = models.BooleanField(default=False)
    expirado = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Solicitud de cambio de email'
        verbose_name_plural = 'Solicitudes de cambio de email'
        indexes = [
            models.Index(fields=['user', 'confirmado']),
            models.Index(fields=['creado']),
        ]

    def __str__(self):
        return f"Cambio email {self.user.username} → {self.nuevo_email}"

    @property
    def esta_vigente(self):
        from datetime import timedelta
        return (
            not self.confirmado
            and not self.expirado
            and (timezone.now() - self.creado) < timedelta(hours=24)
        )
