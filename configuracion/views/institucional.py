from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, UpdateView

from core.decorators import group_required
from core.mixins import GroupRequiredMixin, TimestampedSuccessUrlMixin
from core.models import Institucion

from ..forms import InstitucionForm
from ..selectors import build_institucion_detail_context, get_instituciones_queryset_for_user

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
        context.update(build_institucion_detail_context(institucion))
        return context
