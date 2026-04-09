from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

from ..models_programas import DerivacionPrograma
from ..models_institucional import DerivacionCiudadano, EstadoDerivacionCiudadano
from ..services import DerivacionProgramaService, DerivacionCiudadanoService


# ============================================================================
# VISTAS ACTIVAS — operan sobre DerivacionCiudadano (US-012)
# ============================================================================

@login_required
@require_http_methods(["POST"])
def aceptar_derivacion_ciudadano(request, derivacion_id):
    """Acepta una DerivacionCiudadano creando la InscripcionPrograma."""
    derivacion = get_object_or_404(DerivacionCiudadano, id=derivacion_id)

    if derivacion.estado != EstadoDerivacionCiudadano.PENDIENTE:
        messages.warning(request, 'Esta derivación ya fue procesada.')
        return _redirect_programa_ciudadano(derivacion)

    try:
        inscripcion, creada = DerivacionCiudadanoService.aceptar_derivacion_programa(
            derivacion_id=derivacion.id,
            usuario=request.user,
        )
        if creada:
            messages.success(
                request,
                f'Derivación aceptada. Inscripción creada: {inscripcion.codigo}.',
            )
        else:
            messages.info(
                request,
                f'Derivación aceptada. El ciudadano ya tenía inscripción activa: {inscripcion.codigo}.',
            )
    except ValidationError as exc:
        messages.error(request, exc.messages[0])
    except Exception as exc:
        messages.error(request, f'Error al aceptar derivación: {exc}')

    return _redirect_programa_ciudadano(derivacion)


@login_required
def rechazar_derivacion_ciudadano(request, derivacion_id):
    """Rechaza una DerivacionCiudadano con motivo obligatorio."""
    derivacion = get_object_or_404(DerivacionCiudadano, id=derivacion_id)

    if derivacion.estado != EstadoDerivacionCiudadano.PENDIENTE:
        messages.warning(request, 'Esta derivación ya fue procesada.')
        return _redirect_programa_ciudadano(derivacion)

    if request.method == 'POST':
        motivo = request.POST.get('motivo_rechazo', '').strip()
        if not motivo:
            messages.error(request, 'El motivo de rechazo es obligatorio.')
            return render(request, 'legajos/derivar_rechazar_ciudadano.html', {'derivacion': derivacion})

        try:
            DerivacionCiudadanoService.rechazar_derivacion_programa(
                derivacion_id=derivacion.id,
                usuario=request.user,
                motivo_rechazo=motivo,
            )
            messages.success(request, 'Derivación rechazada.')
        except ValidationError as exc:
            messages.error(request, exc.messages[0])
        except Exception as exc:
            messages.error(request, f'Error al rechazar derivación: {exc}')

        return _redirect_programa_ciudadano(derivacion)

    return render(request, 'legajos/derivar_rechazar_ciudadano.html', {'derivacion': derivacion})


def _redirect_programa_ciudadano(derivacion):
    if derivacion.programa:
        from ..models_programas import Programa
        try:
            return redirect('legajos:programa_detalle', pk=derivacion.programa.id)
        except Exception:
            pass
    return redirect('legajos:programas')


# ============================================================================
# VISTAS LEGACY — operan sobre DerivacionPrograma (Ñachec — no tocar)
# ============================================================================

@login_required
def aceptar_derivacion_programa(request, derivacion_id):
    derivacion = get_object_or_404(DerivacionPrograma, id=derivacion_id)

    if derivacion.estado != 'PENDIENTE':
        messages.warning(request, 'Esta derivación ya fue procesada.')
        return redirect('legajos:programa_detalle', pk=derivacion.programa_destino.id)

    # Si es Ñachec, mostrar modal de validación
    if derivacion.programa_destino.tipo in ['NACHEC', 'ÑACHEC']:
        if request.method == 'GET':
            return render(
                request,
                'legajos/nachec/modal_aceptar_derivacion.html',
                DerivacionProgramaService.build_nachec_acceptance_context(derivacion),
            )

        if request.method == 'POST':
            try:
                result = DerivacionProgramaService.accept_nachec_derivacion(
                    derivacion_id=derivacion.id,
                    usuario=request.user,
                    payload=request.POST,
                )
                getattr(messages, result.status)(request, result.message)
            except ValidationError as exc:
                messages.error(request, exc.messages[0])
                return redirect('legajos:derivacion_aceptar', derivacion_id=derivacion_id)
            except Exception as exc:
                messages.error(request, f'Error al aceptar derivación: {exc}')

            return redirect('legajos:programa_detalle', pk=derivacion.programa_destino.id)

    # Flujo normal legacy
    try:
        result = DerivacionProgramaService.accept_derivacion(
            derivacion_id=derivacion.id,
            usuario=request.user,
        )
        messages.success(request, result.message)
    except ValidationError as exc:
        messages.error(request, exc.messages[0])
    except Exception as exc:
        messages.error(request, f'Error al aceptar derivación: {exc}')

    return redirect('legajos:programa_detalle', pk=derivacion.programa_destino.id)


@login_required
def rechazar_derivacion_programa(request, derivacion_id):
    derivacion = get_object_or_404(DerivacionPrograma, id=derivacion_id)

    if derivacion.estado != 'PENDIENTE':
        messages.warning(request, 'Esta derivación ya fue procesada.')
        return redirect('legajos:programa_detalle', pk=derivacion.programa_destino.id)

    try:
        result = DerivacionProgramaService.reject_derivacion(
            derivacion_id=derivacion.id,
            usuario=request.user,
            motivo_rechazo='Rechazado desde bandeja de derivaciones',
        )
        messages.success(request, result.message)
    except ValidationError as exc:
        messages.error(request, exc.messages[0])
    except Exception as exc:
        messages.error(request, f'Error al rechazar derivación: {exc}')

    return redirect('legajos:programa_detalle', pk=derivacion.programa_destino.id)
