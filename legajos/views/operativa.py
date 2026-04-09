import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from configuracion.forms import InstitucionForm
from core.models import Institucion

from ..forms import InscribirActividadForm
from ..models import InscriptoActividad, LegajoAtencion, LegajoInstitucional, PlanFortalecimiento, PlanIntervencion


class LegajoInstitucionalListView(LoginRequiredMixin, ListView):
    model = LegajoInstitucional
    template_name = 'legajos/legajo_institucional_list.html'
    context_object_name = 'legajos_institucionales'
    paginate_by = 20

    def get_queryset(self):
        return LegajoInstitucional.objects.select_related('institucion', 'responsable_sedronar').order_by('-fecha_apertura')


class LegajoInstitucionalDetailView(LoginRequiredMixin, DetailView):
    model = LegajoInstitucional
    template_name = 'legajos/legajo_institucional_detail.html'
    context_object_name = 'legajo_institucional'


class LegajoInstitucionalCreateView(LoginRequiredMixin, CreateView):
    model = LegajoInstitucional
    template_name = 'legajos/legajo_institucional_form.html'
    fields = ['institucion', 'responsable_sedronar', 'observaciones']

    def get_initial(self):
        initial = super().get_initial()
        institucion_id = self.request.GET.get('institucion')
        if institucion_id:
            initial['institucion'] = institucion_id
        return initial

    def get_success_url(self):
        return reverse_lazy('legajos:legajo_institucional_detalle', kwargs={'pk': self.object.pk})


class LegajoInstitucionalUpdateView(LoginRequiredMixin, UpdateView):
    model = LegajoInstitucional
    template_name = 'legajos/legajo_institucional_form.html'
    fields = ['estado', 'responsable_sedronar', 'observaciones']

    def get_success_url(self):
        return reverse_lazy('legajos:legajo_institucional_detalle', kwargs={'pk': self.object.pk})


class InstitucionListView(LoginRequiredMixin, ListView):
    model = Institucion
    template_name = 'configuracion/institucion_list.html'
    context_object_name = 'instituciones'
    paginate_by = 20

    def get_queryset(self):
        search = self.request.GET.get('search', '')

        if self.request.user.is_superuser:
            queryset = Institucion.objects.filter(activo=True).prefetch_related('encargados')
        else:
            queryset = Institucion.objects.filter(
                encargados=self.request.user,
                activo=True,
            ).prefetch_related('encargados')

        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(cuit__icontains=search)
            )

        return queryset.order_by('nombre')


class InstitucionCreateView(LoginRequiredMixin, CreateView):
    model = Institucion
    form_class = InstitucionForm
    template_name = 'configuracion/institucion_form.html'
    success_url = reverse_lazy('legajos:instituciones')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'No tiene permisos para crear instituciones.')
            return redirect('legajos:instituciones')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, f'Institución {self.object.nombre} creada exitosamente')

        import time
        return redirect(f'{self.success_url}?t={int(time.time())}')


class InstitucionUpdateView(LoginRequiredMixin, UpdateView):
    model = Institucion
    form_class = InstitucionForm
    template_name = 'configuracion/institucion_form.html'
    success_url = reverse_lazy('legajos:instituciones')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Institucion.objects.prefetch_related('encargados')
        return Institucion.objects.filter(encargados=self.request.user).prefetch_related('encargados')

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, f'Institución {self.object.nombre} actualizada exitosamente')

        import time
        return redirect(f'{self.success_url}?t={int(time.time())}')


class InstitucionDeleteView(LoginRequiredMixin, DeleteView):
    model = Institucion
    template_name = 'configuracion/institucion_confirm_delete.html'
    success_url = reverse_lazy('legajos:instituciones')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Institucion.objects.prefetch_related('encargados')
        return Institucion.objects.filter(encargados=self.request.user).prefetch_related('encargados')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        legajos_problematicos = LegajoAtencion.objects.filter(
            dispositivo=self.object,
            ciudadano__dni='00000000',
        )

        for legajo in legajos_problematicos:
            ciudadano_falso = legajo.ciudadano
            legajo.delete()
            ciudadano_falso.delete()

        return super().delete(request, *args, **kwargs)


@login_required
@require_http_methods(['POST'])
def marcar_etapa_plan(request, pk):
    try:
        plan = get_object_or_404(PlanIntervencion, pk=pk)
        data = json.loads(request.body)
        indice = data.get('indice')
        completada = data.get('completada', False)

        if plan.actividades and 0 <= indice < len(plan.actividades):
            plan.actividades[indice]['completada'] = completada
            plan.save()
            return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'error': 'Índice inválido'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(['GET'])
def actividades_por_institucion(request, institucion_id):
    actividades = PlanFortalecimiento.objects.filter(
        legajo_institucional__institucion_id=institucion_id,
        estado='ACTIVO',
    ).values('id', 'nombre', 'tipo')

    actividades_list = [
        {
            'id': actividad['id'],
            'nombre': actividad['nombre'],
            'tipo_display': dict(PlanFortalecimiento.TipoActividad.choices).get(
                actividad['tipo'],
                actividad['tipo'],
            ),
        }
        for actividad in actividades
    ]

    return JsonResponse({'actividades': actividades_list})


class InscribirActividadView(LoginRequiredMixin, CreateView):
    model = InscriptoActividad
    form_class = InscribirActividadForm
    template_name = 'legajos/inscribir_actividad_form.html'

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
        form.instance.ciudadano = self.legajo.ciudadano
        response = super().form_valid(form)
        messages.success(self.request, f'Ciudadano inscrito exitosamente a {form.instance.actividad.nombre}')
        return response

    def get_success_url(self):
        return reverse_lazy('legajos:actividades_inscrito', kwargs={'legajo_id': self.legajo.id})


class ActividadesInscritoListView(LoginRequiredMixin, ListView):
    model = InscriptoActividad
    template_name = 'legajos/actividades_inscrito_list.html'
    context_object_name = 'inscripciones'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return InscriptoActividad.objects.filter(
            ciudadano=self.legajo.ciudadano
        ).select_related(
            'actividad__legajo_institucional__institucion'
        ).order_by('-fecha_inscripcion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        return context
