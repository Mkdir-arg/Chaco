from datetime import date

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, TemplateView

from portal.models import TurnoCiudadano

from ..forms import AprobarTurnoForm, CancelarTurnoBackofficeForm, RechazarTurnoForm
from ..mixins import OperadorRequiredMixin, TurnoOperarRequiredMixin, operador_required, turno_operar_required
from ..models import ConfiguracionTurnos
from ..selectors_turnos import (
    build_agenda_context,
    build_bandeja_pendientes_context,
    get_backoffice_home_context,
    get_turno_detalle_queryset,
)
from ..services.workflow import TurnoActionError, TurnosBackofficeService


class BackofficeHomeView(OperadorRequiredMixin, TemplateView):
    template_name = 'turnos/backoffice/home.html'

    def get_context_data(self, **kwargs):
        return get_backoffice_home_context()


class AgendaView(TurnoOperarRequiredMixin, TemplateView):
    template_name = 'turnos/backoffice/agenda.html'

    def get_context_data(self, **kwargs):
        hoy = date.today()
        fecha_str = self.request.GET.get('fecha', hoy.isoformat())
        config_id = self.request.GET.get('config')
        try:
            fecha = date.fromisoformat(fecha_str)
        except ValueError:
            fecha = hoy
        estado_filter = self.request.GET.get('estado')
        return build_agenda_context(fecha, config_id=config_id, estado_filter=estado_filter)


class BandejaPendientesView(TurnoOperarRequiredMixin, TemplateView):
    template_name = 'turnos/backoffice/bandeja_pendientes.html'

    def get_context_data(self, **kwargs):
        return build_bandeja_pendientes_context()


class TurnoDetailView(TurnoOperarRequiredMixin, DetailView):
    template_name = 'turnos/backoffice/turno_detalle.html'
    context_object_name = 'turno'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return get_turno_detalle_queryset()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'notas_backoffice' in request.POST:
            TurnosBackofficeService.actualizar_notas(
                self.object, request.POST.get('notas_backoffice', '')
            )
            messages.success(request, 'Notas actualizadas.')
        return redirect('turnos:turno_detalle', pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        turno = self.object
        context.update(
            {
                'form_aprobar': AprobarTurnoForm(),
                'form_rechazar': RechazarTurnoForm(),
                'form_cancelar': CancelarTurnoBackofficeForm(),
                'puede_aprobar': turno.estado == TurnoCiudadano.Estado.PENDIENTE,
                'puede_completar': (
                    turno.estado == TurnoCiudadano.Estado.CONFIRMADO and turno.fecha <= date.today()
                ),
                'puede_cancelar': turno.estado
                in [TurnoCiudadano.Estado.PENDIENTE, TurnoCiudadano.Estado.CONFIRMADO],
            }
        )
        return context


@turno_operar_required
@require_POST
def turno_aprobar(request, pk):
    turno = get_object_or_404(TurnoCiudadano, pk=pk)
    if turno.estado != TurnoCiudadano.Estado.PENDIENTE:
        messages.warning(request, 'Este turno ya fue procesado.')
        return redirect('turnos:turno_detalle', pk=pk)

    form = AprobarTurnoForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Datos inválidos.')
        return redirect('turnos:turno_detalle', pk=pk)

    try:
        turno = TurnosBackofficeService.aprobar_turno(
            pk, request.user, notas=form.cleaned_data.get('notas', '')
        )
    except TurnoActionError as exc:
        messages.warning(request, str(exc))
        return redirect('turnos:turno_detalle', pk=pk)

    messages.success(
        request,
        f'Turno {turno.codigo_turno} confirmado. Se notificó al ciudadano por email.',
    )
    return redirect(request.POST.get('next', 'turnos:bandeja_pendientes'))


@turno_operar_required
@require_POST
def turno_rechazar(request, pk):
    turno = get_object_or_404(TurnoCiudadano, pk=pk)
    if turno.estado != TurnoCiudadano.Estado.PENDIENTE:
        messages.warning(request, 'Este turno ya fue procesado.')
        return redirect('turnos:turno_detalle', pk=pk)

    form = RechazarTurnoForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Debe ingresar un motivo de rechazo.')
        return redirect('turnos:turno_detalle', pk=pk)

    try:
        turno = TurnosBackofficeService.rechazar_turno(pk, request.user, form.cleaned_data['motivo'])
    except TurnoActionError as exc:
        messages.warning(request, str(exc))
        return redirect('turnos:turno_detalle', pk=pk)

    messages.success(request, f'Turno {turno.codigo_turno} rechazado. Se notificó al ciudadano.')
    return redirect(request.POST.get('next', 'turnos:bandeja_pendientes'))


@turno_operar_required
@require_POST
def turno_cancelar(request, pk):
    turno = get_object_or_404(TurnoCiudadano, pk=pk)
    form = CancelarTurnoBackofficeForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Debe ingresar un motivo de cancelación.')
        return redirect('turnos:turno_detalle', pk=pk)

    try:
        turno = TurnosBackofficeService.cancelar_turno(turno, form.cleaned_data['motivo'])
    except TurnoActionError as exc:
        messages.warning(request, str(exc))
        return redirect('turnos:turno_detalle', pk=pk)

    messages.success(request, f'Turno {turno.codigo_turno} cancelado. Se notificó al ciudadano.')
    return redirect('turnos:agenda')


@turno_operar_required
@require_POST
def turno_completar(request, pk):
    turno = get_object_or_404(TurnoCiudadano, pk=pk)
    try:
        turno = TurnosBackofficeService.completar_turno(turno)
    except TurnoActionError as exc:
        messages.warning(request, str(exc))
        return redirect('turnos:turno_detalle', pk=pk)
    messages.success(request, f'Turno {turno.codigo_turno} marcado como completado.')
    return redirect(request.POST.get('next', 'turnos:agenda'))


@operador_required
def api_slots_configuracion(request):
    config_id = request.GET.get('config_id')
    fecha_str = request.GET.get('fecha')

    try:
        config = ConfiguracionTurnos.objects.get(pk=config_id, activo=True)
        fecha = date.fromisoformat(fecha_str)
    except (ConfiguracionTurnos.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'error': 'Parámetros inválidos'}, status=400)

    from ..turnos_utils import get_slots_por_configuracion

    slots = get_slots_por_configuracion(config, fecha)
    return JsonResponse(
        {
            'slots': [
                {
                    'hora_inicio': slot['hora_inicio'].strftime('%H:%M'),
                    'hora_fin': slot['hora_fin'].strftime('%H:%M'),
                    'disponible': slot['disponible'],
                    'cupo_restante': slot['cupo_restante'],
                }
                for slot in slots
            ]
        }
    )


backoffice_home = BackofficeHomeView.as_view()
agenda = AgendaView.as_view()
bandeja_pendientes = BandejaPendientesView.as_view()
turno_detalle = TurnoDetailView.as_view()
