from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView

from core.models import Institucion
from legajos.models import Derivacion, PlanFortalecimiento, StaffActividad

from ..forms import (
    ActividadEditarForm,
    DerivacionRechazoForm,
    InscripcionDirectaForm,
    InscriptoEstadoForm,
    PersonalInstitucionForm,
    StaffActividadForm,
)
from ..selectors import build_actividad_detail_context, search_personal_for_actividad
from legajos.services.actividades import InscripcionError, inscribir_ciudadano_a_actividad

from ..services import ConfiguracionInstitucionalService, ConfiguracionWorkflowError


class ActividadDetailView(LoginRequiredMixin, DetailView):
    model = PlanFortalecimiento
    template_name = 'configuracion/actividad_detail.html'
    context_object_name = 'actividad'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_actividad_detail_context(self.get_object()))
        context['inscripcion_form'] = InscripcionDirectaForm()
        return context


class StaffActividadCreateView(LoginRequiredMixin, CreateView):
    model = StaffActividad
    template_name = 'configuracion/staff_form.html'

    def get_form_class(self):
        return StaffActividadForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        actividad = get_object_or_404(PlanFortalecimiento, pk=self.kwargs['actividad_pk'])
        kwargs['legajo_institucional'] = actividad.legajo_institucional
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('personal_form', PersonalInstitucionForm())
        context['actividad'] = get_object_or_404(PlanFortalecimiento, pk=self.kwargs['actividad_pk'])
        return context

    def post(self, request, *args, **kwargs):
        actividad = get_object_or_404(PlanFortalecimiento, pk=self.kwargs['actividad_pk'])
        self.object = None
        staff_form = StaffActividadForm(request.POST, legajo_institucional=actividad.legajo_institucional)
        personal_form = PersonalInstitucionForm(request.POST)

        if staff_form.is_valid():
            tipo_asignacion = staff_form.cleaned_data['tipo_asignacion']
            if tipo_asignacion == 'nuevo' and not personal_form.is_valid():
                context = self.get_context_data(form=staff_form, personal_form=personal_form)
                return self.render_to_response(context)

            try:
                staff, usuario_creado = ConfiguracionInstitucionalService.assign_staff_to_actividad(
                    actividad,
                    rol_en_actividad=staff_form.cleaned_data['rol_en_actividad'],
                    activo=staff_form.cleaned_data['activo'],
                    usuario=request.user,
                    personal=staff_form.cleaned_data.get('personal'),
                    personal_data=(
                        personal_form.cleaned_data
                        if tipo_asignacion == 'nuevo'
                        else None
                    ),
                )
            except (ConfiguracionWorkflowError, ValidationError) as exc:
                target_form = personal_form if tipo_asignacion == 'nuevo' else staff_form
                target_form.add_error(None, str(exc))
                context = self.get_context_data(form=staff_form, personal_form=personal_form)
                return self.render_to_response(context)

            if usuario_creado:
                messages.success(
                    request,
                    (
                        f"Personal {staff.personal.nombre} {staff.personal.apellido} creado y asignado. "
                        f"Usuario: {usuario_creado.username} (password: {staff.personal.dni})"
                    ),
                )
            else:
                messages.success(
                    request,
                    f'Personal {staff.personal.nombre} {staff.personal.apellido} asignado correctamente',
                )
            return redirect('configuracion:actividad_detalle', pk=actividad.pk)

        context = self.get_context_data()
        context['form'] = staff_form
        context['personal_form'] = personal_form
        return self.render_to_response(context)


class DerivacionAceptarView(LoginRequiredMixin, UpdateView):
    model = None

    def post(self, request, *args, **kwargs):
        try:
            derivacion, _ = ConfiguracionInstitucionalService.aceptar_derivacion(
                kwargs['pk'],
                request.user,
            )
        except ConfiguracionWorkflowError as exc:
            derivacion = get_object_or_404(Derivacion, pk=kwargs['pk'])
            messages.error(request, str(exc))
            return redirect('configuracion:actividad_detalle', pk=derivacion.actividad_destino.pk)

        messages.success(
            request,
            'Derivación aceptada. Ciudadano inscrito en la actividad.',
        )
        return redirect('configuracion:actividad_detalle', pk=derivacion.actividad_destino.pk)


class DerivacionRechazarView(LoginRequiredMixin, UpdateView):
    model = None

    def post(self, request, *args, **kwargs):
        form = DerivacionRechazoForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'No se pudo rechazar la derivación.')
            derivacion = get_object_or_404(Derivacion, pk=kwargs['pk'])
            return redirect('configuracion:actividad_detalle', pk=derivacion.actividad_destino.pk)

        try:
            derivacion = ConfiguracionInstitucionalService.rechazar_derivacion(
                kwargs['pk'],
                request.user,
                form.cleaned_data['motivo'],
            )
        except ConfiguracionWorkflowError as exc:
            derivacion = get_object_or_404(Derivacion, pk=kwargs['pk'])
            messages.error(request, str(exc))
            return redirect('configuracion:actividad_detalle', pk=derivacion.actividad_destino.pk)

        messages.success(request, 'Derivación rechazada correctamente.')
        return redirect('configuracion:actividad_detalle', pk=derivacion.actividad_destino.pk)


class InscriptoEditarView(LoginRequiredMixin, UpdateView):
    model = None
    form_class = InscriptoEstadoForm
    template_name = 'configuracion/inscripto_form.html'

    def get_object(self):
        from legajos.models import InscriptoActividad

        return get_object_or_404(InscriptoActividad, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inscripto'] = self.get_object()
        return context

    def get_form(self, form_class=None):
        return self.form_class(instance=self.get_object(), **self.get_form_kwargs())

    def post(self, request, *args, **kwargs):
        inscripto = self.get_object()
        form = self.form_class(request.POST, instance=inscripto)
        if not form.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, inscripto=inscripto)
            )

        changed = ConfiguracionInstitucionalService.update_inscripto_estado(
            inscripto,
            estado=form.cleaned_data['estado'],
            observaciones=form.cleaned_data['observaciones'],
            usuario=request.user,
        )
        if changed:
            messages.success(
                request,
                f'Estado del inscripto actualizado a {inscripto.get_estado_display()}',
            )
        return redirect('configuracion:actividad_detalle', pk=inscripto.actividad.pk)


class ActividadEditarView(LoginRequiredMixin, UpdateView):
    model = PlanFortalecimiento
    form_class = ActividadEditarForm
    template_name = 'configuracion/actividad_editar_form.html'

    def form_valid(self, form):
        self.object = form.instance
        cambios = ConfiguracionInstitucionalService.update_actividad(
            self.object,
            form.cleaned_data,
            self.request.user,
        )
        if cambios:
            messages.success(self.request, 'Actividad actualizada correctamente')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('configuracion:actividad_detalle', kwargs={'pk': self.object.pk})


class InscripcionDirectaView(LoginRequiredMixin, View):
    def post(self, request, actividad_pk):
        actividad = get_object_or_404(PlanFortalecimiento, pk=actividad_pk)
        form = InscripcionDirectaForm(request.POST)

        if not form.is_valid():
            context = build_actividad_detail_context(actividad)
            context['actividad'] = actividad
            context['inscripcion_form'] = form
            return render(request, 'configuracion/actividad_detail.html', context)

        ciudadano = form.cleaned_data['ciudadano_dni']
        observaciones = form.cleaned_data.get('observaciones', '')

        try:
            inscripto = inscribir_ciudadano_a_actividad(
                actividad=actividad,
                ciudadano=ciudadano,
                usuario=request.user,
                observaciones=observaciones,
            )
        except InscripcionError as exc:
            form.add_error(None, str(exc))
            context = build_actividad_detail_context(actividad)
            context['actividad'] = actividad
            context['inscripcion_form'] = form
            return render(request, 'configuracion/actividad_detail.html', context)

        messages.success(
            request,
            f'{ciudadano.nombre_completo} inscripto correctamente. '
            f'Código: {inscripto.codigo_inscripcion}',
        )
        return redirect('configuracion:actividad_detalle', pk=actividad.pk)


def buscar_personal_ajax(request, actividad_pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autorizado'}, status=401)

    actividad = get_object_or_404(PlanFortalecimiento, pk=actividad_pk)
    query = request.GET.get('q', '').strip()
    personal = search_personal_for_actividad(actividad, query=query)
    resultados = [
        {
            'id': p.id,
            'text': f"{p.apellido}, {p.nombre} - DNI: {p.dni}",
        }
        for p in personal
    ]
    return JsonResponse({'results': resultados})
