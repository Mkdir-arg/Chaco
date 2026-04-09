from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, UpdateView

from legajos.models import PlanFortalecimiento

from ..forms import StaffActividadUpdateForm
from ..services import ConfiguracionInstitucionalService

class StaffEditarView(LoginRequiredMixin, UpdateView):
    model = None
    form_class = StaffActividadUpdateForm
    template_name = 'configuracion/staff_editar_form.html'
    
    def get_object(self):
        from legajos.models import StaffActividad
        return get_object_or_404(StaffActividad, pk=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff'] = self.get_object()
        return context

    def get_form(self, form_class=None):
        return self.form_class(instance=self.get_object(), **self.get_form_kwargs())
    
    def post(self, request, *args, **kwargs):
        staff = self.get_object()
        form = self.form_class(request.POST, instance=staff)
        if not form.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, staff=staff)
            )

        cambios = ConfiguracionInstitucionalService.update_staff(
            staff,
            rol_en_actividad=form.cleaned_data['rol_en_actividad'],
            activo=form.cleaned_data['activo'],
            usuario=request.user,
        )
        if cambios:
            messages.success(request, 'Staff actualizado correctamente')
        return redirect('configuracion:actividad_detalle', pk=staff.actividad.pk)


class StaffDesasignarView(LoginRequiredMixin, UpdateView):
    model = None
    
    def post(self, request, *args, **kwargs):
        from legajos.models import StaffActividad

        staff = get_object_or_404(StaffActividad, pk=kwargs['pk'])
        ConfiguracionInstitucionalService.deactivate_staff(staff, request.user)
        messages.success(
            request,
            f'{staff.personal.nombre} {staff.personal.apellido} desasignado de la actividad',
        )
        return redirect('configuracion:actividad_detalle', pk=staff.actividad.pk)


class AsistenciaView(LoginRequiredMixin, DetailView):
    model = PlanFortalecimiento
    template_name = 'configuracion/asistencia.html'
    context_object_name = 'actividad'
    
    def get_context_data(self, **kwargs):
        from legajos.models import InscriptoActividad, RegistroAsistencia
        from datetime import datetime
        
        context = super().get_context_data(**kwargs)
        actividad = self.get_object()
        
        # Obtener fecha actual o la seleccionada
        fecha_str = self.request.GET.get('fecha')
        if fecha_str:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        else:
            fecha = datetime.now().date()
        
        context['fecha_actual'] = fecha
        
        # Obtener inscritos activos con su asistencia del día
        inscritos = InscriptoActividad.objects.filter(
            actividad=actividad,
            estado__in=['INSCRITO', 'ACTIVO']
        ).select_related('ciudadano', 'actividad').order_by('ciudadano__apellido')
        
        # Agregar asistencia actual a cada inscripto
        for inscripto in inscritos:
            try:
                inscripto.asistencia_actual = RegistroAsistencia.objects.get(
                    inscripto=inscripto,
                    fecha=fecha
                )
            except RegistroAsistencia.DoesNotExist:
                inscripto.asistencia_actual = None
        
        context['inscritos'] = inscritos
        
        return context
    
    def post(self, request, *args, **kwargs):
        from legajos.models import InscriptoActividad, RegistroAsistencia
        from django.contrib import messages
        from datetime import datetime
        
        actividad = self.get_object()
        fecha = datetime.now().date()
        
        contador = 0
        for key, value in request.POST.items():
            if key.startswith('asistencia_'):
                inscripto_id = key.replace('asistencia_', '')
                try:
                    inscripto = InscriptoActividad.objects.get(pk=inscripto_id)
                    RegistroAsistencia.objects.update_or_create(
                        inscripto=inscripto,
                        fecha=fecha,
                        defaults={
                            'estado': value,
                            'registrado_por': request.user
                        }
                    )
                    contador += 1
                except InscriptoActividad.DoesNotExist:
                    pass
        
        messages.success(request, f'Asistencia registrada para {contador} personas')
        return redirect('configuracion:asistencia', pk=actividad.pk)


class TomarAsistenciaView(LoginRequiredMixin, DetailView):
    model = PlanFortalecimiento
    template_name = 'configuracion/tomar_asistencia.html'
    context_object_name = 'actividad'
    
    def get_context_data(self, **kwargs):
        from legajos.models import InscriptoActividad
        from datetime import datetime
        
        context = super().get_context_data(**kwargs)
        actividad = self.get_object()
        
        context['inscritos'] = InscriptoActividad.objects.filter(
            actividad=actividad,
            estado__in=['INSCRITO', 'ACTIVO']
        ).select_related('ciudadano').order_by('ciudadano__apellido')
        
        context['fecha_hoy'] = datetime.now().date()
        context['hora_actual'] = datetime.now().strftime('%H:%M')
        
        return context
    
    def post(self, request, *args, **kwargs):
        from legajos.models import InscriptoActividad, RegistroAsistencia
        from django.contrib import messages
        from datetime import datetime
        
        actividad = self.get_object()
        fecha = datetime.now().date()
        
        contador = 0
        for key, value in request.POST.items():
            if key.startswith('asistencia_'):
                inscripto_id = key.replace('asistencia_', '')
                inscripto = get_object_or_404(InscriptoActividad, pk=inscripto_id)
                obs_key = f'obs_{inscripto_id}'
                observaciones = request.POST.get(obs_key, '')
                
                RegistroAsistencia.objects.update_or_create(
                    inscripto=inscripto,
                    fecha=fecha,
                    defaults={
                        'estado': value,
                        'observaciones': observaciones,
                        'registrado_por': request.user
                    }
                )
                contador += 1
        
        messages.success(request, f'Asistencia registrada para {contador} personas el {fecha.strftime("%d/%m/%Y")} a las {datetime.now().strftime("%H:%M")}')
        return redirect('configuracion:actividad_detalle', pk=actividad.pk)


class RegistrarAsistenciaView(TomarAsistenciaView):
    pass
