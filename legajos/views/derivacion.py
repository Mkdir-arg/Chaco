from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import Ciudadano
from ..models_institucional import DerivacionCiudadano, EstadoDerivacionCiudadano, TipoInicioDerivacion
from ..forms.derivacion import DerivarProgramaForm


@login_required
def derivar_programa_view(request, ciudadano_id):
    """Crea una DerivacionCiudadano al programa seleccionado."""
    ciudadano = get_object_or_404(Ciudadano, id=ciudadano_id)

    puede_inscripcion_directa = (
        request.user.is_superuser
        or request.user.groups.filter(name='programaOperar').exists()
    )

    # Bloquear si ya tiene derivación pendiente al mismo programa (se valida en POST)
    if request.method == 'POST':
        form = DerivarProgramaForm(
            request.POST,
            ciudadano=ciudadano,
            allow_inscripcion_directa=puede_inscripcion_directa,
        )
        if form.is_valid():
            ip = form.cleaned_data['institucion_programa']

            # Bloquear si ya hay derivación pendiente al mismo programa
            pendiente_existente = DerivacionCiudadano.objects.filter(
                ciudadano=ciudadano,
                institucion_programa=ip,
                estado=EstadoDerivacionCiudadano.PENDIENTE,
            ).exists()
            if pendiente_existente:
                messages.warning(
                    request,
                    f'Ya existe una derivación pendiente a {ip.programa.nombre} en {ip.institucion.nombre}.',
                )
                return redirect('legajos:ciudadano_detalle', pk=ciudadano_id)

            # Bloquear si ya está activo en ese programa
            from ..models_programas import InscripcionPrograma
            activo_existente = InscripcionPrograma.objects.filter(
                ciudadano=ciudadano,
                programa=ip.programa,
                estado__in=['ACTIVO', 'EN_SEGUIMIENTO'],
            ).exists()
            if activo_existente:
                messages.warning(
                    request,
                    f'El ciudadano ya está activo en {ip.programa.nombre}.',
                )
                return redirect('legajos:ciudadano_detalle', pk=ciudadano_id)

            derivacion = form.save(commit=False)
            derivacion.ciudadano = ciudadano
            derivacion.derivado_por = request.user
            if not puede_inscripcion_directa:
                derivacion.tipo_inicio = TipoInicioDerivacion.DERIVACION
            derivacion.save()

            messages.success(
                request,
                f'Derivación a {ip.programa.nombre} creada. Estado: Pendiente de aceptación.',
            )
            return redirect('legajos:ciudadano_detalle', pk=ciudadano_id)
    else:
        form = DerivarProgramaForm(
            ciudadano=ciudadano,
            allow_inscripcion_directa=puede_inscripcion_directa,
        )

    context = {
        'ciudadano': ciudadano,
        'form': form,
        'puede_inscripcion_directa': puede_inscripcion_directa,
    }

    return render(request, 'legajos/derivar_programa.html', context)
