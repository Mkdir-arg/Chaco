import csv

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from core.cache_decorators import cache_view
from core.models import DispositivoRed

from ..forms import (
    DerivacionForm,
    EvaluacionInicialForm,
    EventoCriticoForm,
    LegajoCerrarForm,
    LegajoReabrirForm,
    PlanIntervencionForm,
    SeguimientoForm,
)
from ..models import Derivacion, EvaluacionInicial, EventoCritico, LegajoAtencion, PlanIntervencion, SeguimientoContacto
from ..selectors import (
    get_derivaciones_queryset,
    get_dispositivo_derivaciones_queryset,
    get_eventos_dashboard_metrics,
    get_eventos_queryset,
    get_export_legajos_queryset,
    get_legajo_detail_queryset,
    get_legajos_queryset,
    get_legajos_report_stats,
    get_plan_vigente,
    get_planes_queryset,
    get_responsable_candidates,
    get_seguimientos_dashboard_metrics,
    get_seguimientos_queryset,
)
from ..services import LegajoWorkflowService


def _build_actividades_extra_context(request, actividades_base=None):
    actividades_base = actividades_base or []
    if request.method == 'POST':
        actividades = []
        index = 4
        while any(
            field_name in request.POST
            for field_name in (
                f'actividad_{index}',
                f'frecuencia_{index}',
                f'responsable_{index}',
            )
        ):
            actividades.append({
                'accion': request.POST.get(f'actividad_{index}', ''),
                'freq': request.POST.get(f'frecuencia_{index}', ''),
                'responsable': request.POST.get(f'responsable_{index}', ''),
            })
            index += 1
        return actividades
    return actividades_base[3:]


@method_decorator(cache_view(timeout=300), name='dispatch')
class LegajoListView(LoginRequiredMixin, ListView):
    model = LegajoAtencion
    template_name = 'legajos/legajo_list.html'
    context_object_name = 'legajos'
    paginate_by = 20

    def get_queryset(self):
        return get_legajos_queryset(self.request.GET.get('estado', ''))


class LegajoDetailView(LoginRequiredMixin, DetailView):
    model = LegajoAtencion
    template_name = 'legajos/legajo_detail.html'
    context_object_name = 'legajo'

    def get_queryset(self):
        return get_legajo_detail_queryset()


class EvaluacionInicialView(LoginRequiredMixin, UpdateView):
    model = EvaluacionInicial
    form_class = EvaluacionInicialForm
    template_name = 'legajos/evaluacion_form.html'

    def get_object(self, queryset=None):
        legajo_id = self.kwargs.get('legajo_id')
        legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
        return LegajoWorkflowService.get_or_create_evaluacion(legajo)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.object.legajo
        return context

    def form_valid(self, form):
        self.object = LegajoWorkflowService.save_evaluacion_from_form(
            form,
            self.object.legajo,
        )
        messages.success(self.request, 'Evaluación inicial guardada exitosamente.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('legajos:detalle', kwargs={'pk': self.object.legajo.id})


class PlanIntervencionView(LoginRequiredMixin, CreateView):
    model = PlanIntervencion
    form_class = PlanIntervencionForm
    template_name = 'legajos/plan_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        if not hasattr(self.legajo, 'evaluacion'):
            messages.error(request, 'Debe completar la evaluación inicial antes de crear un plan.')
            return redirect('legajos:evaluacion', legajo_id=self.legajo.id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        context['actividades_extra'] = _build_actividades_extra_context(self.request)
        return context

    def form_valid(self, form):
        self.object = LegajoWorkflowService.save_plan_from_form(
            form,
            self.legajo,
            self.request.user,
        )
        messages.success(self.request, 'Plan de intervención creado exitosamente.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('legajos:planes', kwargs={'legajo_id': self.legajo.id})


class SeguimientoCreateView(LoginRequiredMixin, CreateView):
    model = SeguimientoContacto
    form_class = SeguimientoForm
    template_name = 'legajos/seguimiento_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        return context

    def form_valid(self, form):
        self.object = LegajoWorkflowService.save_seguimiento_from_form(
            form,
            self.legajo,
            self.request.user,
        )
        messages.success(self.request, 'Seguimiento registrado exitosamente.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('legajos:seguimientos', kwargs={'legajo_id': self.legajo.id})


class SeguimientoListView(LoginRequiredMixin, ListView):
    model = SeguimientoContacto
    template_name = 'legajos/seguimiento_list.html'
    context_object_name = 'seguimientos'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return get_seguimientos_queryset(self.legajo, self.request.GET.get('tipo', ''))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        context['tipos'] = SeguimientoContacto.TipoContacto.choices
        context.update(get_seguimientos_dashboard_metrics(self.legajo))
        return context


class DerivacionCreateView(LoginRequiredMixin, CreateView):
    model = Derivacion
    form_class = DerivacionForm
    template_name = 'legajos/derivacion_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['legajo'] = self.legajo
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        return context

    def form_valid(self, form):
        self.object = LegajoWorkflowService.save_derivacion_from_form(form, self.legajo)
        messages.success(self.request, 'Derivación creada exitosamente.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('legajos:derivaciones', kwargs={'legajo_id': self.legajo.id})


class EventoCriticoCreateView(LoginRequiredMixin, CreateView):
    model = EventoCritico
    form_class = EventoCriticoForm
    template_name = 'legajos/evento_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        return context

    def form_valid(self, form):
        self.object = LegajoWorkflowService.save_evento_from_form(form, self.legajo)
        messages.warning(self.request, f'Evento crítico registrado: {self.object.get_tipo_display()}')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('legajos:eventos', kwargs={'legajo_id': self.legajo.id})


class DerivacionListView(LoginRequiredMixin, ListView):
    model = Derivacion
    template_name = 'legajos/derivacion_list.html'
    context_object_name = 'derivaciones'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return get_derivaciones_queryset(self.legajo, self.request.GET.get('estado', ''))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        context['estados'] = Derivacion.Estado.choices
        return context


class LegajoCerrarView(LoginRequiredMixin, FormView):
    template_name = 'legajos/legajo_cerrar.html'
    form_class = LegajoCerrarForm

    def get_object(self):
        return get_object_or_404(LegajoAtencion, pk=self.kwargs['pk'])

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        puede_cerrar, _ = self.get_object().puede_cerrar()
        field = form.fields['motivo_cierre']
        field.required = not puede_cerrar
        if not puede_cerrar:
            field.widget.attrs['required'] = True
        else:
            field.widget.attrs.pop('required', None)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        legajo = self.get_object()
        puede, mensaje = legajo.puede_cerrar()
        context['legajo'] = legajo
        context['puede_cerrar'] = puede
        context['mensaje'] = mensaje
        context['requiere_justificacion'] = not puede
        return context

    def form_valid(self, form):
        legajo = self.get_object()
        motivo = form.cleaned_data.get('motivo_cierre', '')

        try:
            LegajoWorkflowService.close_legajo(
                legajo,
                motivo,
                self.request.user,
            )
            messages.success(self.request, f'Legajo {legajo.codigo} cerrado exitosamente.')
            return redirect('legajos:detalle', pk=legajo.pk)
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class LegajoReabrirView(LoginRequiredMixin, FormView):
    template_name = 'legajos/legajo_reabrir.html'
    form_class = LegajoReabrirForm

    def get_object(self):
        return get_object_or_404(LegajoAtencion, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.get_object()
        return context

    def form_valid(self, form):
        legajo = self.get_object()
        try:
            LegajoWorkflowService.reopen_legajo(
                legajo,
                form.cleaned_data['motivo_reapertura'],
                self.request.user,
            )
            messages.success(self.request, f'Legajo {legajo.codigo} reabierto exitosamente.')
            return redirect('legajos:detalle', pk=legajo.pk)
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


@method_decorator(cache_view(timeout=600), name='dispatch')
class ReportesView(LoginRequiredMixin, TemplateView):
    template_name = 'legajos/reportes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = get_legajos_report_stats()
        return context


class DispositivoDerivacionesView(LoginRequiredMixin, ListView):
    model = Derivacion
    template_name = 'legajos/dispositivo_derivaciones.html'
    context_object_name = 'derivaciones'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        self.dispositivo = get_object_or_404(DispositivoRed, pk=kwargs['dispositivo_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return get_dispositivo_derivaciones_queryset(
            self.dispositivo,
            self.request.GET.get('estado', ''),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dispositivo'] = self.dispositivo
        context['estados'] = Derivacion.Estado.choices
        return context


class ExportarCSVView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="legajos_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Codigo', 'Ciudadano_DNI', 'Ciudadano_Nombre', 'Ciudadano_Apellido',
            'Dispositivo', 'Estado', 'Nivel_Riesgo', 'Via_Ingreso',
            'Fecha_Apertura', 'Fecha_Cierre', 'Dias_Admision', 'Plan_Vigente',
        ])

        queryset = get_export_legajos_queryset(
            request.GET.get('estado', ''),
            request.GET.get('riesgo', ''),
        )

        for legajo in queryset:
            writer.writerow([
                legajo.codigo,
                legajo.ciudadano.dni,
                legajo.ciudadano.nombre,
                legajo.ciudadano.apellido,
                legajo.dispositivo.nombre if legajo.dispositivo else '',
                legajo.get_estado_display(),
                legajo.get_nivel_riesgo_display(),
                legajo.get_via_ingreso_display(),
                legajo.fecha_apertura.strftime('%d/%m/%Y'),
                legajo.fecha_cierre.strftime('%d/%m/%Y') if legajo.fecha_cierre else '',
                legajo.dias_desde_admision,
                'Sí' if legajo.plan_vigente else 'No',
            ])

        return response


class CerrarAlertaEventoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        evento_id = request.POST.get('evento_id')

        try:
            evento = EventoCritico.objects.get(id=evento_id)
            LegajoWorkflowService.close_alerta_evento(evento, request.user)
            return JsonResponse({'success': True})
        except EventoCritico.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Evento no encontrado'})
        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class CambiarResponsableView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({'usuarios': get_responsable_candidates()})

    def post(self, request, *args, **kwargs):
        legajo_id = kwargs.get('pk')
        nuevo_responsable_id = request.POST.get('responsable_id')

        try:
            legajo = get_object_or_404(LegajoAtencion, pk=legajo_id)
            from django.contrib.auth.models import User
            nuevo_responsable = get_object_or_404(User, pk=nuevo_responsable_id, is_active=True)

            LegajoWorkflowService.change_legajo_responsable(
                legajo,
                nuevo_responsable,
                request.user,
            )

            return JsonResponse({
                'success': True,
                'nuevo_responsable': nuevo_responsable.get_full_name() or nuevo_responsable.username,
            })
        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class EvaluacionListView(LoginRequiredMixin, TemplateView):
    template_name = 'legajos/evaluacion_list.html'

    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        context['evaluacion'] = getattr(self.legajo, 'evaluacion', None)
        return context


class PlanListView(LoginRequiredMixin, ListView):
    model = PlanIntervencion
    template_name = 'legajos/plan_list.html'
    context_object_name = 'planes'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return get_planes_queryset(self.legajo)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        context['plan_vigente'] = get_plan_vigente(self.legajo)
        return context


class PlanUpdateView(LoginRequiredMixin, UpdateView):
    model = PlanIntervencion
    form_class = PlanIntervencionForm
    template_name = 'legajos/plan_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.object.legajo
        context['editando'] = True
        context['actividades_extra'] = _build_actividades_extra_context(
            self.request,
            self.object.actividades or [],
        )
        return context

    def form_valid(self, form):
        self.object = LegajoWorkflowService.save_plan_from_form(
            form,
            self.object.legajo,
            self.request.user,
        )
        messages.success(self.request, 'Plan de intervención actualizado exitosamente.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('legajos:planes', kwargs={'legajo_id': self.object.legajo.id})


class SeguimientoUpdateView(LoginRequiredMixin, UpdateView):
    model = SeguimientoContacto
    form_class = SeguimientoForm
    template_name = 'legajos/seguimiento_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.object.legajo
        context['editando'] = True
        return context

    def form_valid(self, form):
        self.object = LegajoWorkflowService.save_seguimiento_from_form(
            form,
            self.object.legajo,
            self.request.user,
        )
        messages.success(self.request, 'Seguimiento actualizado exitosamente.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('legajos:seguimientos', kwargs={'legajo_id': self.object.legajo.id})


class DerivacionUpdateView(LoginRequiredMixin, UpdateView):
    model = Derivacion
    form_class = DerivacionForm
    template_name = 'legajos/derivacion_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['legajo'] = self.object.legajo
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.object.legajo
        context['editando'] = True
        return context

    def form_valid(self, form):
        self.object = LegajoWorkflowService.save_derivacion_from_form(
            form,
            self.object.legajo,
        )
        messages.success(self.request, 'Derivación actualizada exitosamente.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('legajos:derivaciones', kwargs={'legajo_id': self.object.legajo.id})


class EventoListView(LoginRequiredMixin, ListView):
    model = EventoCritico
    template_name = 'legajos/evento_list.html'
    context_object_name = 'eventos'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return get_eventos_queryset(self.legajo, self.request.GET.get('tipo', ''))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        context['tipos'] = EventoCritico.TipoEvento.choices
        context.update(get_eventos_dashboard_metrics(self.legajo))
        return context


class EventoUpdateView(LoginRequiredMixin, UpdateView):
    model = EventoCritico
    form_class = EventoCriticoForm
    template_name = 'legajos/evento_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.object.legajo
        context['editando'] = True
        return context

    def form_valid(self, form):
        self.object = LegajoWorkflowService.save_evento_from_form(form, self.object.legajo)
        messages.success(self.request, 'Evento crítico actualizado exitosamente.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('legajos:eventos', kwargs={'legajo_id': self.object.legajo.id})
