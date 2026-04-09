from datetime import date

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, TemplateView, UpdateView

from portal.models import TurnoCiudadano

from ..forms import ConfiguracionTurnosForm, DisponibilidadConfiguracionForm
from ..mixins import AdminTurnosRequiredMixin, admin_turnos_required, operador_required
from ..models import ConfiguracionTurnos, DisponibilidadConfiguracion
from ..selectors_turnos import get_configuraciones_list


class ConfiguracionListView(AdminTurnosRequiredMixin, TemplateView):
    template_name = 'turnos/backoffice/configuracion_lista.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['configs'] = get_configuraciones_list()
        return context


class ConfiguracionCreateView(AdminTurnosRequiredMixin, CreateView):
    model = ConfiguracionTurnos
    form_class = ConfiguracionTurnosForm
    template_name = 'turnos/backoffice/configuracion_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Nueva configuración de turnos', 'accion': 'Crear'})
        return context

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, f'Configuración "{self.object.nombre}" creada correctamente.')
        return redirect('turnos:disponibilidad_grilla', pk=self.object.pk)


class ConfiguracionUpdateView(AdminTurnosRequiredMixin, UpdateView):
    model = ConfiguracionTurnos
    form_class = ConfiguracionTurnosForm
    template_name = 'turnos/backoffice/configuracion_form.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'config': self.object,
                'titulo': f'Editar: {self.object.nombre}',
                'accion': 'Guardar cambios',
            }
        )
        return context

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Configuración actualizada correctamente.')
        return redirect('turnos:disponibilidad_grilla', pk=self.object.pk)


class DisponibilidadGrillaView(AdminTurnosRequiredMixin, TemplateView):
    template_name = 'turnos/backoffice/disponibilidad_grilla.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = get_object_or_404(ConfiguracionTurnos, pk=self.kwargs['pk'])
        disponibilidades = config.disponibilidades.all()
        por_dia = {i: [] for i in range(7)}
        for disp in disponibilidades:
            por_dia[disp.dia_semana].append(disp)
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        context.update(
            {
                'config': config,
                'por_dia': por_dia,
                'dias': list(enumerate(dias)),
            }
        )
        return context


class DisponibilidadCreateView(AdminTurnosRequiredMixin, TemplateView):
    template_name = 'turnos/backoffice/disponibilidad_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.config = get_object_or_404(ConfiguracionTurnos, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form(self):
        if self.request.method == 'POST':
            return DisponibilidadConfiguracionForm(self.request.POST)
        dia = self.request.GET.get('dia')
        initial = {'dia_semana': dia} if dia else {}
        return DisponibilidadConfiguracionForm(initial=initial)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'form': kwargs.get('form', self.get_form()),
                'config': self.config,
                'titulo': 'Agregar franja horaria',
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            disp = form.save(commit=False)
            disp.configuracion = self.config
            existe = DisponibilidadConfiguracion.objects.filter(
                configuracion=self.config,
                dia_semana=disp.dia_semana,
                hora_inicio=disp.hora_inicio,
            ).exists()
            if existe:
                form.add_error('hora_inicio', 'Ya existe una franja para ese día y horario.')
            else:
                disp.save()
                cleaned_data = form.cleaned_data
                slots = cleaned_data.get('_slots_preview', '?')
                resto = cleaned_data.get('_resto_min', 0)
                message = f'Franja agregada. Se generarán {slots} turnos de {disp.duracion_turno_min} min.'
                if resto:
                    message += f' Quedan {resto} min sin cubrir.'
                messages.success(request, message)
                return redirect('turnos:disponibilidad_grilla', pk=self.config.pk)
        return self.render_to_response(self.get_context_data(form=form))


class DisponibilidadUpdateView(AdminTurnosRequiredMixin, UpdateView):
    model = DisponibilidadConfiguracion
    form_class = DisponibilidadConfiguracionForm
    template_name = 'turnos/backoffice/disponibilidad_form.html'
    pk_url_kwarg = 'disp_pk'

    def get_queryset(self):
        return DisponibilidadConfiguracion.objects.filter(configuracion_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'config': get_object_or_404(ConfiguracionTurnos, pk=self.kwargs['pk']),
                'disp': self.object,
                'titulo': 'Editar franja horaria',
            }
        )
        return context

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Franja horaria actualizada.')
        return redirect('turnos:disponibilidad_grilla', pk=self.kwargs['pk'])


@admin_turnos_required
@require_POST
def disponibilidad_eliminar(request, pk, disp_pk):
    config = get_object_or_404(ConfiguracionTurnos, pk=pk)
    disp = get_object_or_404(DisponibilidadConfiguracion, pk=disp_pk, configuracion=config)
    turnos_afectados = TurnoCiudadano.objects.filter(
        configuracion=config,
        fecha__gte=date.today(),
        hora_inicio=disp.hora_inicio,
        estado__in=[TurnoCiudadano.Estado.PENDIENTE, TurnoCiudadano.Estado.CONFIRMADO],
    ).count()

    if turnos_afectados:
        messages.error(
            request,
            f'No se puede eliminar: hay {turnos_afectados} turno(s) futuro(s) en ese horario.',
        )
        return redirect('turnos:disponibilidad_grilla', pk=config.pk)

    disp.delete()
    messages.success(request, 'Franja horaria eliminada.')
    return redirect('turnos:disponibilidad_grilla', pk=config.pk)


configuracion_lista = operador_required(ConfiguracionListView.as_view())
configuracion_crear = ConfiguracionCreateView.as_view()
configuracion_editar = ConfiguracionUpdateView.as_view()
disponibilidad_grilla = DisponibilidadGrillaView.as_view()
disponibilidad_agregar = DisponibilidadCreateView.as_view()
disponibilidad_editar = DisponibilidadUpdateView.as_view()
