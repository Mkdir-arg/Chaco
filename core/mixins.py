from django.contrib import messages
from django.shortcuts import redirect


class GroupRequiredMixin:
    """
    Mixin para CBVs que requieren pertenencia a uno o más grupos Django.
    Redirige con mensaje de error en lugar de lanzar PermissionDenied (403).
    Uso: definir required_groups = ['grupo1', 'grupo2'] en la vista.
    """
    required_groups = []
    redirect_url = '/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if request.user.is_superuser or (
            self.required_groups
            and request.user.groups.filter(name__in=self.required_groups).exists()
        ):
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect(self.redirect_url)


class TimestampedSuccessUrlMixin:
    success_url = None

    def redirect_with_timestamp(self):
        return redirect(f"{self.get_success_url()}?t={self._timestamp_value()}")

    def _timestamp_value(self):
        import time

        return int(time.time())
