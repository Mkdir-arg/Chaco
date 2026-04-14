"""
Vistas para Gestión Operativa de Programas
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.db.models import Count, Q
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from ..models_programas import Programa, InscripcionPrograma
from ..models_institucional import (
    InstitucionPrograma,
    CoordinadorPrograma,
    DerivacionCiudadano,
    CasoInstitucional,
    EstadoDerivacionCiudadano,
    EstadoCaso,
)


class ProgramaListView(LoginRequiredMixin, ListView):
    """
    Lista de programas que el usuario puede gestionar.
    - SuperAdmin: ve todos
    - Coordinador: ve solo sus programas asignados
    """
    model = Programa
    template_name = 'legajos/programas/programa_list.html'
    context_object_name = 'programas'
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            # SuperAdmin ve todos los programas
            queryset = Programa.objects.filter(estado=Programa.Estado.ACTIVO)
        else:
            # Coordinador ve solo sus programas
            queryset = Programa.objects.filter(
                coordinadores__usuario=self.request.user,
                coordinadores__activo=True,
                estado=Programa.Estado.ACTIVO,
            )
        
        # Agregar métricas
        queryset = queryset.annotate(
            total_instituciones=Count('instituciones_habilitadas', filter=Q(instituciones_habilitadas__activo=True)),
            total_derivaciones_pendientes=Count('derivaciones_ciudadanos', filter=Q(derivaciones_ciudadanos__estado=EstadoDerivacionCiudadano.PENDIENTE)),
            total_casos_activos=Count('instituciones_habilitadas__casos', filter=Q(instituciones_habilitadas__casos__estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO]))
        ).order_by('orden', 'nombre')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_superadmin'] = self.request.user.is_superuser
        return context


class ProgramaDetailView(LoginRequiredMixin, DetailView):
    """
    Vista detallada de un programa con 5 solapas operativas:
    1. Dashboard Ejecutivo
    2. Bandeja de Derivaciones
    3. Ciudadanos en Atención
    4. Instituciones Participantes
    5. Indicadores
    """
    model = Programa
    template_name = 'legajos/programas/programa_detail.html'
    context_object_name = 'programa'
    
    def get_template_names(self):
        """Usar template específico para Ñachec"""
        programa = self.get_object()
        if programa.tipo in ['NACHEC', 'ÑACHEC']:
            return ['legajos/programas/programa_nachec_detail.html']
        return ['legajos/programas/programa_detail.html']
    
    def dispatch(self, request, *args, **kwargs):
        # Permitir acceso a todos los usuarios autenticados temporalmente
        # TODO: Restaurar verificación de permisos cuando se asignen coordinadores
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        programa = self.get_object()
        
        # Si es Ñachec, cargar datos específicos
        if programa.tipo in ['NACHEC', 'ÑACHEC']:
            from ..models_nachec import CasoNachec
            from ..models_programas import DerivacionPrograma
            
            # Filtros
            estado_filtro = self.request.GET.get('estado')
            urgencia_filtro = self.request.GET.get('urgencia')
            busqueda = self.request.GET.get('q')
            
            # Derivaciones de ciudadanos (igual que programa 1)
            derivaciones_qs = DerivacionPrograma.objects.filter(
                programa_destino=programa
            ).select_related('ciudadano', 'programa_origen', 'derivado_por')
            
            # Aplicar filtros
            if estado_filtro:
                derivaciones_qs = derivaciones_qs.filter(estado=estado_filtro)
            if urgencia_filtro:
                derivaciones_qs = derivaciones_qs.filter(urgencia=urgencia_filtro)
            if busqueda:
                derivaciones_qs = derivaciones_qs.filter(
                    Q(ciudadano__nombre__icontains=busqueda) |
                    Q(ciudadano__apellido__icontains=busqueda) |
                    Q(ciudadano__numero_documento__icontains=busqueda)
                )
            
            context['derivaciones_ciudadanos'] = derivaciones_qs.order_by('-creado')[:50]
            
            # Stats de derivaciones ciudadanos (siempre globales)
            context['stats_ciudadanos'] = {
                'pendientes': DerivacionPrograma.objects.filter(programa_destino=programa, estado='PENDIENTE').count(),
                'aceptadas': DerivacionPrograma.objects.filter(programa_destino=programa, estado='ACEPTADA').count(),
                'rechazadas': DerivacionPrograma.objects.filter(programa_destino=programa, estado='RECHAZADA').count(),
            }
            
            # Filtros activos
            context['filtros_activos'] = {
                'estado': estado_filtro,
                'urgencia': urgencia_filtro,
                'busqueda': busqueda
            }
            
            # Casos Ñachec para otras pestañas
            from ..models_nachec import TareaNachec
            casos_nachec = CasoNachec.objects.select_related(
                'ciudadano_titular', 'operador_admision', 'territorial'
            ).order_by('-fecha_derivacion')
            
            # Agregar información de tarea de validación a cada caso
            for caso in casos_nachec:
                tarea = TareaNachec.objects.filter(caso=caso, tipo='VALIDACION', estado='COMPLETADA').first()
                caso.tarea_validacion_completada = bool(tarea)
            
            context['casos_nachec'] = casos_nachec
            
            # Métricas del dashboard analítico
            from django.db.models import Avg
            from ..models_nachec import PrestacionNachec, PlanIntervencionNachec, EvaluacionVulnerabilidad, RelevamientoNachec
            from datetime import timedelta
            
            hoy = timezone.now().date()
            
            # Fase 1: Captación
            derivaciones_totales = casos_nachec.count()
            derivaciones_aceptadas = casos_nachec.exclude(estado='RECHAZADO').count()
            tasa_aceptacion = round((derivaciones_aceptadas / derivaciones_totales * 100) if derivaciones_totales > 0 else 0, 1)
            
            # Fase 2: Asignación
            relevamientos_completados = RelevamientoNachec.objects.filter(caso__in=casos_nachec, completado=True).count()
            casos_sin_asignar = casos_nachec.filter(estado='A_ASIGNAR').count()
            
            # Fase 3: Evaluación
            evaluaciones = EvaluacionVulnerabilidad.objects.filter(caso__in=casos_nachec)
            scoring_alto = evaluaciones.filter(categoria_final='ALTO').count()
            scoring_medio = evaluaciones.filter(categoria_final='MEDIO').count()
            scoring_bajo = evaluaciones.filter(categoria_final='BAJO').count()
            planes_activos = PlanIntervencionNachec.objects.filter(caso__in=casos_nachec, vigente=True).count()
            
            # Fase 4: Ejecución
            prestaciones_qs = PrestacionNachec.objects.filter(caso__in=casos_nachec)
            prestaciones_entregadas = prestaciones_qs.filter(estado='ENTREGADA').count()
            prestaciones_programadas = prestaciones_qs.filter(estado='PROGRAMADA').count()
            
            # Cumplimiento SLA
            prestaciones_con_sla = prestaciones_qs.filter(estado='ENTREGADA', sla_hasta__isnull=False, fecha_entregada__isnull=False)
            cumplidas = sum(1 for p in prestaciones_con_sla if p.fecha_entregada and p.sla_hasta and 
                            timezone.make_aware(timezone.datetime.combine(p.fecha_entregada, timezone.datetime.min.time())) <= p.sla_hasta)
            cumplimiento_sla = round((cumplidas / prestaciones_con_sla.count() * 100) if prestaciones_con_sla.count() > 0 else 0, 1)
            
            # Fase 5: Seguimiento
            casos_cerrados = casos_nachec.filter(estado='CERRADO').count()
            
            # Impacto
            familias_asistidas = casos_nachec.filter(estado__in=['EN_EJECUCION', 'EN_SEGUIMIENTO', 'CERRADO']).count()
            score_promedio = round(evaluaciones.aggregate(Avg('score_total'))['score_total__avg'] or 0, 1)
            
            context['stats_nachec'] = {
                'derivados': CasoNachec.objects.filter(estado='DERIVADO').count(),
                'en_revision': CasoNachec.objects.filter(estado='EN_REVISION').count(),
                'asignados': CasoNachec.objects.filter(estado='ASIGNADO').count(),
                'en_relevamiento': CasoNachec.objects.filter(estado='EN_RELEVAMIENTO').count(),
                'evaluados': CasoNachec.objects.filter(estado='EVALUADO').count(),
                'en_seguimiento': CasoNachec.objects.filter(estado='EN_SEGUIMIENTO').count(),
            }
            
            # Dashboard analítico
            context['dashboard_metricas'] = {
                'derivaciones_totales': derivaciones_totales,
                'tasa_aceptacion': tasa_aceptacion,
                'relevamientos_completados': relevamientos_completados,
                'casos_sin_asignar': casos_sin_asignar,
                'scoring_alto': scoring_alto,
                'scoring_medio': scoring_medio,
                'scoring_bajo': scoring_bajo,
                'planes_activos': planes_activos,
                'prestaciones_entregadas': prestaciones_entregadas,
                'prestaciones_programadas': prestaciones_programadas,
                'cumplimiento_sla': cumplimiento_sla,
                'casos_cerrados': casos_cerrados,
                'familias_asistidas': familias_asistidas,
                'score_promedio': score_promedio
            }
            
            # PASO 8: Prestaciones activas
            from ..models_nachec import PrestacionNachec
            
            # Filtrar prestaciones donde el usuario es responsable o coordinador del caso
            prestaciones_qs = PrestacionNachec.objects.filter(
                Q(responsable=self.request.user) | Q(caso__coordinador=self.request.user)
            ).select_related(
                'caso__ciudadano_titular',
                'responsable',
                'plan'
            ).order_by('-fecha_programada')
            
            context['prestaciones_nachec'] = prestaciones_qs
            
            return context
        
        # Métricas del dashboard
        instituciones_habilitadas = InstitucionPrograma.objects.filter(
            programa=programa,
            activo=True
        ).select_related('institucion')
        
        context['total_instituciones'] = instituciones_habilitadas.count()
        
        context['total_derivaciones_pendientes'] = DerivacionCiudadano.objects.filter(
            programa=programa,
            estado=EstadoDerivacionCiudadano.PENDIENTE,
        ).count()
        
        context['total_casos_activos'] = CasoInstitucional.objects.filter(
            institucion_programa__programa=programa,
            estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO]
        ).count()
        
        context['total_casos_totales'] = CasoInstitucional.objects.filter(
            institucion_programa__programa=programa
        ).count()
        
        # BANDEJA DE DERIVACIONES (ciudadanos) — usa DerivacionCiudadano (US-012)
        from ..models_programas import InscripcionPrograma

        context['derivaciones_ciudadanos'] = DerivacionCiudadano.objects.filter(
            programa=programa
        ).select_related('ciudadano', 'programa_origen', 'derivado_por', 'institucion_programa__institucion').order_by('-creado')[:20]

        context['stats_ciudadanos'] = {
            'pendientes': DerivacionCiudadano.objects.filter(programa=programa, estado=EstadoDerivacionCiudadano.PENDIENTE).count(),
            'aceptadas': DerivacionCiudadano.objects.filter(programa=programa, estado=EstadoDerivacionCiudadano.ACEPTADA).count(),
            'rechazadas': DerivacionCiudadano.objects.filter(programa=programa, estado=EstadoDerivacionCiudadano.RECHAZADA).count(),
        }
        
        # Derivaciones institucionales
        context['derivaciones_institucionales'] = DerivacionCiudadano.objects.filter(
            programa=programa
        ).select_related('ciudadano', 'institucion', 'derivado_por').order_by('-creado')[:20]
        
        # Instituciones participantes
        context['instituciones'] = instituciones_habilitadas.annotate(
            casos_activos=Count('casos', filter=Q(casos__estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO])),
            derivaciones_pendientes=Count('derivaciones', filter=Q(derivaciones__estado=EstadoDerivacionCiudadano.PENDIENTE))
        )
        
        # Casos activos
        context['casos_activos'] = CasoInstitucional.objects.filter(
            institucion_programa__programa=programa,
            estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO]
        ).select_related('ciudadano', 'institucion_programa__institucion', 'responsable').order_by('-fecha_apertura')[:20]
        
        # ACOMPAÑAMIENTOS
        acompanamientos = InscripcionPrograma.objects.filter(
            programa=programa
        ).select_related('ciudadano', 'responsable').order_by('-fecha_inscripcion')
        
        # Anotar institución desde CasoInstitucional si existe
        acompanamientos_list = []
        for insc in acompanamientos:
            caso = CasoInstitucional.objects.filter(
                ciudadano=insc.ciudadano,
                institucion_programa__programa=programa
            ).select_related('institucion_programa__institucion').first()
            
            insc.institucion_nombre = caso.institucion_programa.institucion.nombre if caso else None
            acompanamientos_list.append(insc)
        
        context['acompanamientos'] = acompanamientos_list
        context['total_acompanamientos_activos'] = InscripcionPrograma.objects.filter(
            programa=programa,
            estado__in=['ACTIVO', 'EN_SEGUIMIENTO']
        ).count()
        
        context['stats_acompanamientos'] = {
            'activos': InscripcionPrograma.objects.filter(programa=programa, estado='ACTIVO').count(),
            'seguimiento': InscripcionPrograma.objects.filter(programa=programa, estado='EN_SEGUIMIENTO').count(),
            'cerrados': InscripcionPrograma.objects.filter(programa=programa, estado='CERRADO').count(),
            'bajas': InscripcionPrograma.objects.filter(programa=programa, estado='DADO_DE_BAJA').count(),
        }
        
        # DASHBOARD
        total_derivaciones = (
            context['stats_ciudadanos']['pendientes']
            + context['stats_ciudadanos']['aceptadas']
            + context['stats_ciudadanos']['rechazadas']
        )
        context['total_derivaciones'] = total_derivaciones if total_derivaciones > 0 else 1
        context['tasa_aceptacion'] = round((context['stats_ciudadanos']['aceptadas'] / context['total_derivaciones']) * 100) if context['total_derivaciones'] > 1 else 0
        
        # Top instituciones
        top_inst = instituciones_habilitadas.annotate(
            casos_activos=Count('casos', filter=Q(casos__estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO]))
        ).order_by('-casos_activos')[:5]
        context['top_instituciones'] = top_inst
        context['max_casos_institucion'] = top_inst.first().casos_activos if top_inst.exists() and top_inst.first().casos_activos > 0 else 1
        
        # Últimas derivaciones
        context['ultimas_derivaciones'] = DerivacionCiudadano.objects.filter(
            programa=programa
        ).select_related('ciudadano').order_by('-creado')[:5]
        
        # INDICADORES
        context['promedio_casos_institucion'] = round(context['total_casos_activos'] / context['total_instituciones']) if context['total_instituciones'] > 0 else 0
        context['total_acompanamientos_totales'] = InscripcionPrograma.objects.filter(programa=programa).count()
        
        context['es_superadmin'] = self.request.user.is_superuser

        return context


@login_required
@require_http_methods(["POST"])
def dar_de_baja_inscripcion(request, inscripcion_id):
    """
    Da de baja a un ciudadano de un programa persistente.
    Espera campo POST 'motivo' (obligatorio).
    """
    from ..services.programas import BajaProgramaService

    inscripcion = get_object_or_404(InscripcionPrograma, id=inscripcion_id)
    motivo = request.POST.get('motivo', '').strip()

    if not motivo:
        messages.error(request, "Debe ingresar un motivo para la baja.")
        return redirect('legajos:programa_detalle', pk=inscripcion.programa_id)

    try:
        BajaProgramaService.dar_de_baja(
            inscripcion_id=inscripcion_id,
            usuario=request.user,
            motivo=motivo,
        )
        messages.success(
            request,
            f"{inscripcion.ciudadano.nombre_completo} fue dado de baja del programa correctamente.",
        )
    except ValueError as exc:
        messages.error(request, str(exc))

    return redirect('legajos:programa_detalle', pk=inscripcion.programa_id)
