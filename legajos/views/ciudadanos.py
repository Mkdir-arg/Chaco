from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from core.cache_decorators import cache_view, invalidate_cache_pattern
from core.models import DispositivoRed

from ..forms import (
    AdmisionLegajoForm,
    BuscarCiudadanoForm,
    CiudadanoConfirmarForm,
    CiudadanoManualForm,
    CiudadanoUpdateForm,
    ConsultaRenaperForm,
    ConsentimientoForm,
)
from ..models import Ciudadano, LegajoAtencion
from ..selectors import (
    build_ciudadano_detail_context,
    get_ciudadanos_dashboard_metrics,
    get_ciudadanos_queryset,
)
from ..services import AdmisionSessionService, CiudadanosService


@method_decorator(cache_view(timeout=300), name='dispatch')
class CiudadanoListView(LoginRequiredMixin, ListView):
    model = Ciudadano
    template_name = 'legajos/ciudadano_list.html'
    context_object_name = 'ciudadanos'
    paginate_by = 20

    def get_queryset(self):
        return get_ciudadanos_queryset(self.request.GET.get('search', ''))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['metricas'] = get_ciudadanos_dashboard_metrics()
        return context


class CiudadanoDetailView(LoginRequiredMixin, DetailView):
    model = Ciudadano
    template_name = 'legajos/ciudadano_detail.html'
    context_object_name = 'ciudadano'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_ciudadano_detail_context(self.object, user=self.request.user))
        return context


class CiudadanoCreateView(LoginRequiredMixin, FormView):
    template_name = 'legajos/ciudadano_renaper_form.html'
    form_class = ConsultaRenaperForm

    def form_valid(self, form):
        dni = form.cleaned_data['dni']
        sexo = form.cleaned_data['sexo']

        if Ciudadano.objects.filter(dni=dni).exists():
            messages.error(self.request, f'Ya existe un ciudadano con DNI {dni}')
            return self.form_invalid(form)

        resultado = CiudadanosService.consultar_renaper(dni, sexo)

        if not resultado['success']:
            context = self.get_context_data(form=form)
            context['renaper_error'] = True
            context['dni_consultado'] = dni
            context['sexo_consultado'] = sexo

            if resultado.get('fallecido'):
                context['error_message'] = 'La persona consultada figura como fallecida en RENAPER'
            else:
                context['error_message'] = (
                    f'No se encontraron datos en RENAPER: '
                    f'{resultado.get("error", "Error desconocido")}'
                )

            return self.render_to_response(context)

        CiudadanosService.store_renaper_data(self.request.session, resultado)
        return redirect('legajos:ciudadano_confirmar')


class CiudadanoManualView(LoginRequiredMixin, CreateView):
    model = Ciudadano
    form_class = CiudadanoManualForm
    template_name = 'legajos/ciudadano_manual_form.html'
    success_url = reverse_lazy('legajos:ciudadanos')

    def get_initial(self):
        initial = super().get_initial()
        cuit = self.request.GET.get('cuit') or self.request.GET.get('dni')
        sexo = self.request.GET.get('sexo')

        if cuit:
            initial['dni'] = (
                CiudadanosService.extract_dni_from_cuit(cuit)
                or ''.join(filter(str.isdigit, cuit))
            )
        if sexo:
            initial['genero'] = sexo
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        CiudadanosService.invalidate_ciudadanos_cache()
        messages.success(
            self.request,
            f'Ciudadano {self.object.nombre} {self.object.apellido} creado exitosamente (carga manual)',
        )

        import time
        return redirect(f'{self.success_url}?t={int(time.time())}')


class CiudadanoConfirmarView(LoginRequiredMixin, CreateView):
    model = Ciudadano
    form_class = CiudadanoConfirmarForm
    template_name = 'legajos/ciudadano_confirmar_form.html'
    success_url = reverse_lazy('legajos:ciudadanos')

    def dispatch(self, request, *args, **kwargs):
        if not CiudadanosService.get_renaper_data(request.session):
            messages.error(request, 'No hay datos de RENAPER disponibles. Inicie el proceso nuevamente.')
            return redirect('legajos:ciudadano_nuevo')
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        datos = CiudadanosService.get_renaper_data(self.request.session)
        return {
            'dni': datos.get('dni'),
            'nombre': datos.get('nombre'),
            'apellido': datos.get('apellido'),
            'fecha_nacimiento': datos.get('fecha_nacimiento'),
            'genero': datos.get('genero'),
            'domicilio': datos.get('domicilio'),
            'provincia': datos.get('provincia'),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datos_api'] = CiudadanosService.get_renaper_raw_data(self.request.session)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        CiudadanosService.clear_renaper_data(self.request.session)
        CiudadanosService.invalidate_ciudadanos_cache()
        messages.success(
            self.request,
            f'Ciudadano {self.object.nombre} {self.object.apellido} creado exitosamente',
        )

        import time
        return redirect(f'{self.success_url}?t={int(time.time())}')


class CiudadanoUpdateView(LoginRequiredMixin, UpdateView):
    model = Ciudadano
    form_class = CiudadanoUpdateForm
    template_name = 'legajos/ciudadano_edit_form.html'

    def _puede_ver_sensible(self):
        user = self.request.user
        return user.is_superuser or user.groups.filter(name='ciudadanoSensible').exists()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['puede_ver_sensible'] = self._puede_ver_sensible()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puede_ver_sensible'] = self._puede_ver_sensible()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        CiudadanosService.invalidate_ciudadanos_cache()
        return response

    def get_success_url(self):
        return reverse_lazy('legajos:ciudadano_detalle', kwargs={'pk': self.object.pk})


class LegajoCreateView(LoginRequiredMixin, CreateView):
    model = LegajoAtencion
    form_class = AdmisionLegajoForm
    template_name = 'legajos/legajo_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ciudadanos'] = Ciudadano.objects.filter(activo=True).order_by('apellido', 'nombre')
        return context

    def form_valid(self, form):
        form.instance.responsable = self.request.user
        response = super().form_valid(form)

        invalidate_cache_pattern('legajos_list')
        from dashboard.utils import invalidate_dashboard_cache
        invalidate_dashboard_cache()

        messages.success(self.request, f'Legajo {self.object.codigo} creado exitosamente.')
        return response

    def get_success_url(self):
        return reverse_lazy('legajos:detalle', kwargs={'pk': self.object.pk})


class AdmisionPaso1View(LoginRequiredMixin, FormView):
    template_name = 'legajos/admision_paso1.html'
    form_class = BuscarCiudadanoForm

    def get(self, request, *args, **kwargs):
        ciudadano_id = request.GET.get('ciudadano')
        if ciudadano_id:
            try:
                ciudadano = Ciudadano.objects.get(id=ciudadano_id, activo=True)
                AdmisionSessionService.set_ciudadano_id(request.session, ciudadano.id)
                return redirect('legajos:admision_paso2')
            except Ciudadano.DoesNotExist:
                messages.error(request, 'Ciudadano no encontrado')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        dni = form.cleaned_data['dni']
        try:
            ciudadano = Ciudadano.objects.get(dni=dni, activo=True)
            AdmisionSessionService.set_ciudadano_id(self.request.session, ciudadano.id)
            return redirect('legajos:admision_paso2')
        except Ciudadano.DoesNotExist:
            messages.error(
                self.request,
                f'No se encontró un ciudadano con DNI {dni}. Debe crear el ciudadano primero.',
            )
            return self.form_invalid(form)


class AdmisionPaso2View(LoginRequiredMixin, CreateView):
    model = LegajoAtencion
    form_class = AdmisionLegajoForm
    template_name = 'legajos/admision_paso2.html'

    def dispatch(self, request, *args, **kwargs):
        if not AdmisionSessionService.get_ciudadano_id(request.session):
            messages.error(request, 'Debe seleccionar un ciudadano primero.')
            return redirect('legajos:admision_paso1')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ciudadano'] = AdmisionSessionService.get_ciudadano_from_session(
            self.request.session
        )
        if self.request.user.is_superuser:
            context['debug_dispositivos'] = True
            context['total_dispositivos'] = DispositivoRed.objects.filter(activo=True).count()
        return context

    def form_valid(self, form):
        try:
            self.object = AdmisionSessionService.create_legajo_from_form(
                form,
                self.request.session,
                self.request.user,
            )
            return redirect('legajos:admision_paso3')
        except Exception as e:
            messages.error(self.request, f'Error al crear el legajo: {str(e)}')
            return self.form_invalid(form)


class AdmisionPaso3View(LoginRequiredMixin, FormView):
    template_name = 'legajos/admision_paso3.html'
    form_class = ConsentimientoForm

    def dispatch(self, request, *args, **kwargs):
        if not AdmisionSessionService.get_legajo_id(request.session):
            messages.error(request, 'Proceso de admisión inválido.')
            return redirect('legajos:admision_paso1')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = AdmisionSessionService.get_legajo_from_session(
            self.request.session
        )
        return context

    def form_valid(self, form):
        legajo, _ = AdmisionSessionService.create_consentimiento_from_form(
            form,
            self.request.session,
        )
        messages.success(self.request, f'Legajo {legajo.codigo} creado exitosamente con consentimiento.')
        return redirect('legajos:detalle', pk=legajo.id)

    def get(self, request, *args, **kwargs):
        if request.GET.get('skip') == '1':
            legajo = AdmisionSessionService.finalize_without_consent(request.session)
            messages.success(request, f'Legajo {legajo.codigo} creado exitosamente.')
            return redirect('legajos:detalle', pk=legajo.id)

        return super().get(request, *args, **kwargs)
