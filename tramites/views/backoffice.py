from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse


def es_staff(user):
    return user.is_superuser or user.is_staff or user.groups.filter(
        name__in=["Administrador", "Supervisor"]
    ).exists()


@login_required
@user_passes_test(es_staff)
def lista_tramites(request):
    return JsonResponse(
        {"error": "DEPRECATED: módulo de trámites institucionales retirado."},
        status=410,
    )


@login_required
@user_passes_test(es_staff)
def detalle_tramite(request, tramite_id):
    return JsonResponse(
        {"error": "DEPRECATED: módulo de trámites institucionales retirado."},
        status=410,
    )


@login_required
@user_passes_test(es_staff)
def aprobar_tramite(request, tramite_id):
    return JsonResponse(
        {"error": "DEPRECATED: módulo de trámites institucionales retirado."},
        status=410,
    )


@login_required
@user_passes_test(es_staff)
def rechazar_tramite(request, tramite_id):
    return JsonResponse(
        {"error": "DEPRECATED: módulo de trámites institucionales retirado."},
        status=410,
    )
