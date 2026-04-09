"""
API JSON para el motor de flujos (US-006).
Endpoints sin DRF — FBVs que devuelven JsonResponse.
"""
import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from core.decorators import group_required
from legajos.models_programas import Programa

from .forms import DefinicionFlujoForm
from .models import Flujo, InstanciaFlujo, VersionFlujo

logger = logging.getLogger(__name__)


def _tiene_permiso_editar(user):
    return user.groups.filter(name='programaConfigurar').exists() or user.is_superuser


@login_required
@require_http_methods(['GET', 'POST'])
def api_definicion(request, programa_id):
    programa = get_object_or_404(Programa, pk=programa_id)

    if request.method == 'GET':
        try:
            flujo = programa.flujo
        except Flujo.DoesNotExist:
            return JsonResponse({'definicion': None, 'version': None})

        version = flujo.versiones.filter(estado=VersionFlujo.Estado.PUBLICADA).order_by('-numero_version').first()
        if not version:
            version = flujo.versiones.order_by('-numero_version').first()
        if not version:
            return JsonResponse({'definicion': None, 'version': None})

        return JsonResponse({
            'definicion': version.definicion,
            'version_id': version.pk,
            'numero_version': version.numero_version,
            'estado': version.estado,
        })

    # POST — guardar nueva versión borrador
    if not _tiene_permiso_editar(request.user):
        return JsonResponse({'error': 'Sin permiso.'}, status=403)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'JSON inválido.'}, status=400)

    form = DefinicionFlujoForm({'definicion': body})
    if not form.is_valid():
        return JsonResponse({'error': form.errors['definicion'][0]}, status=400)

    flujo, _ = Flujo.objects.get_or_create(
        programa=programa,
        defaults={'nombre': f'Flujo — {programa.nombre}'},
    )
    version = VersionFlujo.objects.create(
        flujo=flujo,
        definicion=form.cleaned_data['definicion'],
        creado_por=request.user,
    )

    return JsonResponse({
        'ok': True,
        'version_id': version.pk,
        'numero_version': version.numero_version,
    })


@login_required
@require_http_methods(['POST'])
def api_publicar(request, programa_id):
    if not _tiene_permiso_editar(request.user):
        return JsonResponse({'error': 'Sin permiso.'}, status=403)

    programa = get_object_or_404(Programa, pk=programa_id)

    try:
        flujo = programa.flujo
    except Flujo.DoesNotExist:
        return JsonResponse({'error': 'El programa no tiene flujo definido.'}, status=400)

    from django.db import transaction
    with transaction.atomic():
        borrador = (
            flujo.versiones
            .select_for_update()
            .filter(estado=VersionFlujo.Estado.BORRADOR)
            .order_by('-numero_version')
            .first()
        )
        if not borrador:
            return JsonResponse({'error': 'No hay versión borrador para publicar.'}, status=400)

        flujo.versiones.filter(estado=VersionFlujo.Estado.PUBLICADA).update(
            estado=VersionFlujo.Estado.ARCHIVADA
        )
        borrador.estado = VersionFlujo.Estado.PUBLICADA
        borrador.fecha_publicacion = timezone.now()
        borrador.save(update_fields=['estado', 'fecha_publicacion'])

    return JsonResponse({'ok': True, 'version_id': borrador.pk})


@login_required
@require_http_methods(['GET'])
def api_instancia(request, instancia_id):
    if not _tiene_permiso_editar(request.user):
        return JsonResponse({'error': 'Sin permiso.'}, status=403)

    instancia = get_object_or_404(InstanciaFlujo, pk=instancia_id)

    definicion = instancia.version_flujo.definicion
    nodo = next(
        (n for n in definicion.get('nodos', []) if n['id'] == instancia.nodo_actual),
        None,
    )

    return JsonResponse({
        'instancia_id': instancia.pk,
        'nodo_actual': instancia.nodo_actual,
        'nodo': nodo,
        'estado': instancia.estado,
        'fecha_inicio': instancia.fecha_inicio.isoformat(),
        'fecha_cierre': instancia.fecha_cierre.isoformat() if instancia.fecha_cierre else None,
    })


# ---------------------------------------------------------------------------
# Editor visual (US-007)
# ---------------------------------------------------------------------------

@login_required
@group_required(['programaConfigurar'])
def editor_flujo(request, programa_id):
    programa = get_object_or_404(Programa, pk=programa_id)

    instancias_activas = 0
    try:
        version_publicada = programa.flujo_activo
        if version_publicada:
            from .models import InstanciaFlujo as _IF
            instancias_activas = _IF.objects.filter(
                version_flujo=version_publicada,
                estado=_IF.Estado.ACTIVA,
            ).count()
    except Exception:
        pass

    return render(request, 'flujos/editor.html', {
        'programa': programa,
        'instancias_activas': instancias_activas,
        'api_definicion_url': reverse('flujos:api_definicion', kwargs={'programa_id': programa_id}),
        'api_publicar_url': reverse('flujos:api_publicar', kwargs={'programa_id': programa_id}),
    })
