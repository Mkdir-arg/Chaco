from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.decorators import group_required
from core.mixins import GroupRequiredMixin, TimestampedSuccessUrlMixin
from core.models import Institucion
from legajos.models import (
    EvaluacionInstitucional,
    IndicadorInstitucional,
    PersonalInstitucion,
    PlanFortalecimiento,
)

from ..forms import InstitucionForm, PlanFortalecimientoForm
from ..selectors import build_institucion_detail_context, get_instituciones_queryset_for_user
from ..services import ConfiguracionInstitucionalService

_INST_VER = ['institucionVer', 'institucionAdministrar']
_INST_ADMIN = ['institucionAdministrar']
_REDIRECT = 'configuracion:dispositivos'


class InstitucionListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Institucion
    template_name = 'configuracion/institucion_list.html'
    context_object_name = 'instituciones'
    paginate_by = 20
    required_groups = _INST_VER
    redirect_url = '/'

    def get_queryset(self):
        return get_instituciones_queryset_for_user(
            self.request.user,
            search=self.request.GET.get('search', ''),
        )


DispositivoListView = InstitucionListView
DispositivoRed = Institucion
DispositivoForm = InstitucionForm


class InstitucionCreateView(LoginRequiredMixin, GroupRequiredMixin, TimestampedSuccessUrlMixin, CreateView):
    model = Institucion
    form_class = InstitucionForm
    template_name = 'configuracion/institucion_form.html'
    success_url = reverse_lazy('configuracion:dispositivos')
    required_groups = _INST_ADMIN
    redirect_url = '/'

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, f'Institución {self.object.nombre} creada exitosamente')
        return self.redirect_with_timestamp()


DispositivoCreateView = InstitucionCreateView


class InstitucionUpdateView(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = Institucion
    form_class = InstitucionForm
    template_name = 'configuracion/institucion_form.html'
    success_url = reverse_lazy('configuracion:dispositivos')
    required_groups = _INST_ADMIN
    redirect_url = '/'

    def get_queryset(self):
        return Institucion.objects.select_related(
            'provincia', 'municipio', 'localidad'
        ).prefetch_related('encargados')


DispositivoUpdateView = InstitucionUpdateView


class InstitucionDeleteView(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = Institucion
    template_name = 'configuracion/institucion_confirm_delete.html'
    success_url = reverse_lazy('configuracion:dispositivos')
    required_groups = _INST_ADMIN
    redirect_url = '/'

    def get_queryset(self):
        return Institucion.objects.select_related(
            'provincia', 'municipio', 'localidad'
        ).prefetch_related('encargados')


class InstitucionDetailView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = Institucion
    template_name = 'configuracion/institucion_detail.html'
    context_object_name = 'institucion'
    required_groups = _INST_VER
    redirect_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        institucion = self.get_object()
        ConfiguracionInstitucionalService.ensure_legajo_institucional(institucion)
        context.update(build_institucion_detail_context(institucion))
        return context


class PersonalInstitucionCreateView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = PersonalInstitucion
    fields = ['nombre', 'apellido', 'dni', 'tipo', 'titulo_profesional', 'matricula', 'activo']
    template_name = 'configuracion/personal_form.html'
    required_groups = _INST_ADMIN
    redirect_url = '/'

    def form_valid(self, form):
        institucion = get_object_or_404(Institucion, pk=self.kwargs['institucion_pk'])
        form.instance.legajo_institucional = (
            ConfiguracionInstitucionalService.ensure_legajo_institucional(institucion)
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('configuracion:institucion_detalle', kwargs={'pk': self.kwargs['institucion_pk']})


class EvaluacionInstitucionCreateView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = EvaluacionInstitucional
    fields = ['fecha_evaluacion', 'observaciones']
    template_name = 'configuracion/evaluacion_form.html'
    required_groups = _INST_ADMIN
    redirect_url = '/'

    def form_valid(self, form):
        institucion = get_object_or_404(Institucion, pk=self.kwargs['institucion_pk'])
        form.instance.legajo_institucional = (
            ConfiguracionInstitucionalService.ensure_legajo_institucional(institucion)
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('configuracion:institucion_detalle', kwargs={'pk': self.kwargs['institucion_pk']})


class PlanFortalecimientoCreateView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = PlanFortalecimiento
    form_class = PlanFortalecimientoForm
    template_name = 'configuracion/plan_form.html'
    required_groups = _INST_ADMIN
    redirect_url = '/'

    def form_valid(self, form):
        institucion = get_object_or_404(Institucion, pk=self.kwargs['institucion_pk'])
        form.instance.legajo_institucional = (
            ConfiguracionInstitucionalService.ensure_legajo_institucional(institucion)
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('configuracion:institucion_detalle', kwargs={'pk': self.kwargs['institucion_pk']})


class IndicadorInstitucionCreateView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = IndicadorInstitucional
    fields = ['periodo', 'observaciones']
    template_name = 'configuracion/indicador_form.html'
    required_groups = _INST_ADMIN
    redirect_url = '/'

    def form_valid(self, form):
        institucion = get_object_or_404(Institucion, pk=self.kwargs['institucion_pk'])
        form.instance.legajo_institucional = (
            ConfiguracionInstitucionalService.ensure_legajo_institucional(institucion)
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('configuracion:institucion_detalle', kwargs={'pk': self.kwargs['institucion_pk']})


@login_required
@group_required(['institucionAdministrar'], redirect_to='configuracion:dispositivos')
def documento_subir(request, pk):
    if request.method == 'POST':
        messages.info(request, 'La funcionalidad de documentos estará disponible próximamente')
    return redirect('configuracion:institucion_detalle', pk=pk)
