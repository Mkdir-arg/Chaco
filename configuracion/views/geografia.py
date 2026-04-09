from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.mixins import TimestampedSuccessUrlMixin
from core.models import Localidad, Municipio, Provincia

from ..forms import LocalidadForm, MunicipioForm, ProvinciaForm


class ProvinciaListView(LoginRequiredMixin, ListView):
    model = Provincia
    template_name = 'configuracion/provincia_list.html'
    context_object_name = 'provincias'
    paginate_by = 20


class ProvinciaCreateView(LoginRequiredMixin, TimestampedSuccessUrlMixin, CreateView):
    model = Provincia
    form_class = ProvinciaForm
    template_name = 'configuracion/provincia_form.html'
    success_url = reverse_lazy('configuracion:provincias')

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class ProvinciaUpdateView(LoginRequiredMixin, TimestampedSuccessUrlMixin, UpdateView):
    model = Provincia
    form_class = ProvinciaForm
    template_name = 'configuracion/provincia_form.html'
    success_url = reverse_lazy('configuracion:provincias')

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class ProvinciaDeleteView(LoginRequiredMixin, DeleteView):
    model = Provincia
    template_name = 'configuracion/provincia_confirm_delete.html'
    success_url = reverse_lazy('configuracion:provincias')


class MunicipioListView(LoginRequiredMixin, ListView):
    model = Municipio
    template_name = 'configuracion/municipio_list.html'
    context_object_name = 'municipios'
    paginate_by = 20


class MunicipioCreateView(LoginRequiredMixin, TimestampedSuccessUrlMixin, CreateView):
    model = Municipio
    form_class = MunicipioForm
    template_name = 'configuracion/municipio_form.html'
    success_url = reverse_lazy('configuracion:municipios')

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class MunicipioUpdateView(LoginRequiredMixin, TimestampedSuccessUrlMixin, UpdateView):
    model = Municipio
    form_class = MunicipioForm
    template_name = 'configuracion/municipio_form.html'
    success_url = reverse_lazy('configuracion:municipios')

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class MunicipioDeleteView(LoginRequiredMixin, DeleteView):
    model = Municipio
    template_name = 'configuracion/municipio_confirm_delete.html'
    success_url = reverse_lazy('configuracion:municipios')


class LocalidadListView(LoginRequiredMixin, ListView):
    model = Localidad
    template_name = 'configuracion/localidad_list.html'
    context_object_name = 'localidades'
    paginate_by = 20


class LocalidadCreateView(LoginRequiredMixin, TimestampedSuccessUrlMixin, CreateView):
    model = Localidad
    form_class = LocalidadForm
    template_name = 'configuracion/localidad_form.html'
    success_url = reverse_lazy('configuracion:localidades')

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class LocalidadUpdateView(LoginRequiredMixin, TimestampedSuccessUrlMixin, UpdateView):
    model = Localidad
    form_class = LocalidadForm
    template_name = 'configuracion/localidad_form.html'
    success_url = reverse_lazy('configuracion:localidades')

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class LocalidadDeleteView(LoginRequiredMixin, DeleteView):
    model = Localidad
    template_name = 'configuracion/localidad_confirm_delete.html'
    success_url = reverse_lazy('configuracion:localidades')
