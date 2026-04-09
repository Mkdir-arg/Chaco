from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


def es_operador(user):
    return user.is_authenticated and (
        user.is_staff or user.is_superuser or not user.groups.filter(name='Ciudadanos').exists()
    )


def operador_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not es_operador(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return login_required(_wrapped)


def admin_turnos_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not (
            request.user.is_superuser
            or request.user.groups.filter(name='turnoConfigurar').exists()
        ):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return login_required(_wrapped)


class OperadorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return es_operador(self.request.user)

    def handle_no_permission(self):
        raise PermissionDenied


class AdminTurnosRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_superuser or user.groups.filter(name='turnoConfigurar').exists()
        )

    def handle_no_permission(self):
        raise PermissionDenied


def turno_operar_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not (
            request.user.is_superuser
            or request.user.groups.filter(name='turnoOperar').exists()
        ):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return login_required(_wrapped)


class TurnoOperarRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_superuser or user.groups.filter(name='turnoOperar').exists()
        )

    def handle_no_permission(self):
        raise PermissionDenied
