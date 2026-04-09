from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.mixins import GroupRequiredMixin
from core.models import Secretaria, Subsecretaria

from ..forms_secretaria import SecretariaForm, SubsecretariaForm

_GRUPOS = ['secretariaConfigurar']
_REDIRECT = '/'


class SecretariaListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Secretaria
    template_name = 'configuracion/secretaria_list.html'
    context_object_name = 'secretarias'
    required_groups = _GRUPOS
    redirect_url = _REDIRECT

    def get_queryset(self):
        qs = Secretaria.objects.annotate(cant_subsecretarias=Count('subsecretarias'))
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(nombre__icontains=search)
        return qs.order_by('nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class SecretariaCreateView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Secretaria
    form_class = SecretariaForm
    template_name = 'configuracion/secretaria_form.html'
    success_url = reverse_lazy('configuracion:secretarias')
    required_groups = _GRUPOS
    redirect_url = _REDIRECT

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Secretaría "{self.object.nombre}" creada exitosamente.')
        return response


class SecretariaUpdateView(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = Secretaria
    form_class = SecretariaForm
    template_name = 'configuracion/secretaria_form.html'
    success_url = reverse_lazy('configuracion:secretarias')
    required_groups = _GRUPOS
    redirect_url = _REDIRECT

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Secretaría "{self.object.nombre}" actualizada.')
        return response


class SecretariaDeleteView(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = Secretaria
    template_name = 'configuracion/secretaria_confirm_delete.html'
    success_url = reverse_lazy('configuracion:secretarias')
    required_groups = _GRUPOS
    redirect_url = _REDIRECT

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            nombre = self.object.nombre
            self.object.delete()
            messages.success(request, f'Secretaría "{nombre}" eliminada.')
            return redirect(self.success_url)
        except ProtectedError:
            messages.error(request, 'No se puede eliminar esta secretaría porque tiene subsecretarías asociadas.')
            return redirect(self.success_url)


class SubsecretariaListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Subsecretaria
    template_name = 'configuracion/subsecretaria_list.html'
    context_object_name = 'subsecretarias'
    required_groups = _GRUPOS
    redirect_url = _REDIRECT

    def get_queryset(self):
        qs = Subsecretaria.objects.select_related('secretaria').annotate(
            cant_programas=Count('programa')
        )
        secretaria_id = self.request.GET.get('secretaria')
        if secretaria_id:
            qs = qs.filter(secretaria_id=secretaria_id)
        return qs.order_by('secretaria__nombre', 'nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['secretarias'] = Secretaria.objects.filter(activo=True).order_by('nombre')
        context['secretaria_filtro'] = self.request.GET.get('secretaria', '')
        return context


class SubsecretariaCreateView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Subsecretaria
    form_class = SubsecretariaForm
    template_name = 'configuracion/subsecretaria_form.html'
    success_url = reverse_lazy('configuracion:subsecretarias')
    required_groups = _GRUPOS
    redirect_url = _REDIRECT

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Subsecretaría "{self.object.nombre}" creada exitosamente.')
        return response


class SubsecretariaUpdateView(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = Subsecretaria
    form_class = SubsecretariaForm
    template_name = 'configuracion/subsecretaria_form.html'
    success_url = reverse_lazy('configuracion:subsecretarias')
    required_groups = _GRUPOS
    redirect_url = _REDIRECT

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Subsecretaría "{self.object.nombre}" actualizada.')
        return response


class SubsecretariaDeleteView(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = Subsecretaria
    template_name = 'configuracion/subsecretaria_confirm_delete.html'
    success_url = reverse_lazy('configuracion:subsecretarias')
    required_groups = _GRUPOS
    redirect_url = _REDIRECT

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            nombre = self.object.nombre
            self.object.delete()
            messages.success(request, f'Subsecretaría "{nombre}" eliminada.')
            return redirect(self.success_url)
        except ProtectedError:
            messages.error(request, 'No se puede eliminar esta subsecretaría porque tiene programas asociados.')
            return redirect(self.success_url)
