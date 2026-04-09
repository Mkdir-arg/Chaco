from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from legajos.models import ClaseActividad, PlanFortalecimiento

from ..forms.clases import ClaseActividadForm
from ..selectors.clases import build_clase_asistencia_context, get_clases_de_actividad
from ..services.clases import ClaseError, crear_clase, editar_clase, eliminar_clase, guardar_asistencia_clase


class ClaseListView(LoginRequiredMixin, View):
    template_name = 'configuracion/clase_lista.html'

    def get(self, request, pk):
        actividad = get_object_or_404(PlanFortalecimiento, pk=pk)
        clases = get_clases_de_actividad(actividad)
        return render(request, self.template_name, {
            'actividad': actividad,
            'clases': clases,
        })


class ClaseCreateView(LoginRequiredMixin, View):
    template_name = 'configuracion/clase_form.html'

    def get(self, request, actividad_pk):
        actividad = get_object_or_404(PlanFortalecimiento, pk=actividad_pk)
        form = ClaseActividadForm()
        return render(request, self.template_name, {'actividad': actividad, 'form': form})

    def post(self, request, actividad_pk):
        actividad = get_object_or_404(PlanFortalecimiento, pk=actividad_pk)
        form = ClaseActividadForm(request.POST)
        form._actividad = actividad

        if not form.is_valid():
            return render(request, self.template_name, {'actividad': actividad, 'form': form})

        cd = form.cleaned_data
        try:
            crear_clase(
                actividad=actividad,
                fecha=cd['fecha'],
                hora_inicio=cd['hora_inicio'],
                duracion_minutos=cd.get('duracion_minutos'),
                titulo=cd.get('titulo', ''),
                usuario=request.user,
            )
        except Exception as exc:
            form.add_error(None, str(exc))
            return render(request, self.template_name, {'actividad': actividad, 'form': form})

        messages.success(request, 'Clase creada correctamente.')
        return redirect('configuracion:clase_lista', pk=actividad.pk)


class ClaseEditarView(LoginRequiredMixin, View):
    template_name = 'configuracion/clase_form.html'

    def get(self, request, pk):
        clase = get_object_or_404(ClaseActividad, pk=pk)
        form = ClaseActividadForm(instance=clase)
        return render(request, self.template_name, {'actividad': clase.actividad, 'form': form, 'clase': clase})

    def post(self, request, pk):
        clase = get_object_or_404(ClaseActividad, pk=pk)
        form = ClaseActividadForm(request.POST, instance=clase)

        if not form.is_valid():
            return render(request, self.template_name, {'actividad': clase.actividad, 'form': form, 'clase': clase})

        cd = form.cleaned_data
        try:
            editar_clase(
                clase=clase,
                fecha=cd['fecha'],
                hora_inicio=cd['hora_inicio'],
                duracion_minutos=cd.get('duracion_minutos'),
                titulo=cd.get('titulo', ''),
                usuario=request.user,
            )
        except Exception as exc:
            form.add_error(None, str(exc))
            return render(request, self.template_name, {'actividad': clase.actividad, 'form': form, 'clase': clase})

        messages.success(request, 'Clase actualizada correctamente.')
        return redirect('configuracion:clase_lista', pk=clase.actividad.pk)


class ClaseEliminarView(LoginRequiredMixin, View):
    def post(self, request, pk):
        clase = get_object_or_404(ClaseActividad, pk=pk)
        actividad_pk = clase.actividad.pk
        try:
            eliminar_clase(clase)
            messages.success(request, 'Clase eliminada correctamente.')
        except ClaseError as exc:
            messages.error(request, str(exc))
        return redirect('configuracion:clase_lista', pk=actividad_pk)


class ClaseAsistenciaView(LoginRequiredMixin, View):
    template_name = 'configuracion/clase_asistencia.html'

    def get(self, request, pk):
        clase = get_object_or_404(ClaseActividad, pk=pk)
        context = build_clase_asistencia_context(clase)
        return render(request, self.template_name, context)

    def post(self, request, pk):
        clase = get_object_or_404(ClaseActividad, pk=pk)

        if clase.fecha > timezone.localdate():
            messages.error(request, 'No se puede registrar asistencia en una clase futura.')
            return redirect('configuracion:clase_asistencia', pk=clase.pk)

        # Construir dict {inscripcion_id: estado} desde el POST
        registros = {}
        for key, value in request.POST.items():
            if key.startswith('asistencia_'):
                try:
                    inscripcion_id = int(key.replace('asistencia_', ''))
                    registros[inscripcion_id] = value
                except ValueError:
                    pass

        try:
            cantidad = guardar_asistencia_clase(clase=clase, registros=registros, usuario=request.user)
            messages.success(request, f'Asistencia registrada para {cantidad} ciudadano(s).')
        except ClaseError as exc:
            messages.error(request, str(exc))

        return redirect('configuracion:clase_asistencia', pk=clase.pk)
