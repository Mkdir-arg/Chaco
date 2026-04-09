from functools import wraps

from django.core.exceptions import PermissionDenied


def group_required(group_names, redirect_to=None):
    """
    Permite el acceso solo a usuarios autenticados que pertenezcan a alguno de los grupos indicados,
    o que sean superusuarios.

    Si se pasa redirect_to, redirige con messages.error en lugar de lanzar PermissionDenied.
    Sin redirect_to: comportamiento original (PermissionDenied / 403).
    """

    def in_group(user):
        return user.is_authenticated and (
            user.groups.filter(name__in=group_names).exists() or user.is_superuser
        )

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not in_group(request.user):
                if redirect_to:
                    from django.contrib import messages
                    from django.shortcuts import redirect
                    messages.error(request, 'No tiene permisos para acceder a esta sección.')
                    return redirect(redirect_to)
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def ciudadano_required(view_func):
    """Permite acceso solo a usuarios del grupo Ciudadanos. Redirige al login del portal."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('portal:ciudadano_login')
        if not request.user.groups.filter(name='Ciudadanos').exists():
            from django.shortcuts import redirect
            return redirect('portal:ciudadano_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
