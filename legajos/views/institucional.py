"""
Vistas para Sistema NODO - Gestión Programática Institucional
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Avg, Sum, F
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import json

from core.models import Institucion
from ..models import LegajoInstitucional
from ..models_institucional import (
    InstitucionPrograma,
    DerivacionCiudadano,
    DerivacionInstitucional,
    CasoInstitucional,
    EstadoDerivacionCiudadano,
    EstadoDerivacion,
    EstadoCaso,
    EstadoPrograma,
)
from ..forms import (
    DerivacionInstitucionalForm,
    RechazarDerivacionForm,
    CambiarEstadoCasoForm,
)
from ..services import CasoService, DerivacionCiudadanoService, DerivacionService
from core.decorators import group_required
from ..permissions_institucional import (
    puede_ver_programa,
    puede_operar_programa,
    require_operar_programa
)


@login_required
@group_required(['institucionVer', 'institucionAdministrar'], redirect_to='configuracion:dispositivos')
def institucion_detalle_programatico(request, pk):
    """
    Vista principal de detalle institucional con solapas dinámicas por programa.
    Genera solapas estáticas + dinámicas según programas activos.
    """
    institucion = get_object_or_404(Institucion, pk=pk)
    
    # Obtener o crear legajo institucional
    legajo, created = LegajoInstitucional.objects.get_or_create(
        institucion=institucion,
        defaults={'responsable_sedronar': request.user}
    )
    
    # Solapas estáticas
    solapas = [
        {'id': 'resumen', 'nombre': 'Resumen', 'icono': 'dashboard', 'orden': 1, 'tipo': 'estatica'},
        {'id': 'personal', 'nombre': 'Personal', 'icono': 'people', 'orden': 2, 'tipo': 'estatica'},
        {'id': 'evaluaciones', 'nombre': 'Evaluaciones', 'icono': 'assessment', 'orden': 3, 'tipo': 'estatica'},
        {'id': 'documentos', 'nombre': 'Documentos', 'icono': 'folder', 'orden': 4, 'tipo': 'estatica'},
    ]
    
    # Solapas dinámicas (programas activos con anotaciones optimizadas)
    programas_activos = InstitucionPrograma.objects.filter(
        institucion=institucion,
        activo=True,
        estado_programa=EstadoPrograma.ACTIVO
    ).select_related('programa').annotate(
        derivaciones_pendientes=Count(
            'derivaciones',
            filter=Q(derivaciones__estado=EstadoDerivacion.PENDIENTE)
        ),
        casos_activos=Count(
            'casos',
            filter=Q(casos__estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO])
        )
    ).order_by('programa__orden')
    
    for ip in programas_activos:
        # Verificar si el usuario puede ver este programa
        if puede_ver_programa(ip, request.user):
            solapas.append({
                'id': f'programa_{ip.programa.id}',
                'nombre': ip.programa.nombre,
                'icono': ip.programa.icono,
                'color': ip.programa.color,
                'orden': 100 + ip.programa.orden,
                'tipo': 'programa',
                'badge_derivaciones': ip.derivaciones_pendientes,
                'badge_casos': ip.casos_activos,
                'institucion_programa_id': ip.id,
                'puede_operar': puede_operar_programa(ip, request.user)
            })
    
    # Ordenar solapas
    solapas = sorted(solapas, key=lambda x: x['orden'])
    
    # Métricas consolidadas para resumen
    total_derivaciones_pendientes = sum(s.get('badge_derivaciones', 0) for s in solapas if s['tipo'] == 'programa')
    total_casos_activos = sum(s.get('badge_casos', 0) for s in solapas if s['tipo'] == 'programa')
    total_programas_activos = len([s for s in solapas if s['tipo'] == 'programa'])
    
    # Métricas adicionales para dashboard
    hoy = timezone.now().date()
    hace_30_dias = hoy - timedelta(days=30)
    hace_7_dias = hoy - timedelta(days=7)
    
    # Derivaciones por estado
    derivaciones_stats = DerivacionCiudadano.objects.filter(
        institucion=institucion
    ).aggregate(
        total=Count('id'),
        pendientes=Count('id', filter=Q(estado=EstadoDerivacionCiudadano.PENDIENTE)),
        aceptadas=Count('id', filter=Q(estado=EstadoDerivacionCiudadano.ACEPTADA)),
        rechazadas=Count('id', filter=Q(estado=EstadoDerivacionCiudadano.RECHAZADA)),
        ultimos_30_dias=Count('id', filter=Q(creado__gte=hace_30_dias)),
        ultimos_7_dias=Count('id', filter=Q(creado__gte=hace_7_dias))
    )
    
    # Casos por estado
    casos_stats = CasoInstitucional.objects.filter(
        institucion_programa__institucion=institucion
    ).aggregate(
        total=Count('id'),
        activos=Count('id', filter=Q(estado=EstadoCaso.ACTIVO)),
        seguimiento=Count('id', filter=Q(estado=EstadoCaso.EN_SEGUIMIENTO)),
        egresados=Count('id', filter=Q(estado=EstadoCaso.EGRESADO)),
        cerrados=Count('id', filter=Q(estado=EstadoCaso.CERRADO)),
        suspendidos=Count('id', filter=Q(estado=EstadoCaso.SUSPENDIDO))
    )
    
    # Casos por programa
    casos_por_programa = CasoInstitucional.objects.filter(
        institucion_programa__institucion=institucion,
        estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO]
    ).values(
        'institucion_programa__programa__nombre'
    ).annotate(
        cantidad=Count('id')
    ).order_by('-cantidad')[:5]
    
    # Derivaciones por urgencia
    derivaciones_urgencia = DerivacionCiudadano.objects.filter(
        institucion=institucion,
        estado=EstadoDerivacionCiudadano.PENDIENTE,
    ).values('urgencia').annotate(
        cantidad=Count('id')
    )

    # Tendencia de derivaciones (últimos 6 meses)
    meses_atras = [hoy - timedelta(days=30*i) for i in range(6)]
    derivaciones_tendencia = []
    for mes in reversed(meses_atras):
        mes_siguiente = mes + timedelta(days=30)
        count = DerivacionCiudadano.objects.filter(
            institucion=institucion,
            creado__gte=mes,
            creado__lt=mes_siguiente,
        ).count()
        derivaciones_tendencia.append({
            'mes': mes.strftime('%b'),
            'cantidad': count
        })
    
    # Tasa de aceptación
    total_respondidas = derivaciones_stats['aceptadas'] + derivaciones_stats['rechazadas']
    tasa_aceptacion = round((derivaciones_stats['aceptadas'] / total_respondidas * 100) if total_respondidas > 0 else 0, 1)
    
    # Tiempo promedio de respuesta (últimas 30 derivaciones respondidas)
    derivaciones_recientes = DerivacionCiudadano.objects.filter(
        institucion=institucion,
        estado__in=[EstadoDerivacionCiudadano.ACEPTADA, EstadoDerivacionCiudadano.RECHAZADA],
        fecha_respuesta__isnull=False,
    ).order_by('-fecha_respuesta')[:30]
    
    tiempos_respuesta = []
    for d in derivaciones_recientes:
        if d.fecha_respuesta:
            delta = d.fecha_respuesta - d.creado
            tiempos_respuesta.append(delta.total_seconds() / 3600)  # en horas
    
    tiempo_promedio_respuesta = round(sum(tiempos_respuesta) / len(tiempos_respuesta), 1) if tiempos_respuesta else 0
    
    # Documentos institucionales (simulados por ahora)
    documentos = {
        'convenios': [],
        'habilitaciones': [],
        'evaluaciones': [],
        'otros': [],
        'todos': []
    }
    
    context = {
        'institucion': institucion,
        'legajo': legajo,
        'solapas': solapas,
        'total_derivaciones_pendientes': total_derivaciones_pendientes,
        'total_casos_activos': total_casos_activos,
        'total_programas_activos': total_programas_activos,
        # Nuevas métricas
        'derivaciones_stats': derivaciones_stats,
        'casos_stats': casos_stats,
        'casos_por_programa': json.dumps(list(casos_por_programa)),
        'derivaciones_urgencia': list(derivaciones_urgencia),
        'derivaciones_tendencia': json.dumps(derivaciones_tendencia),
        'tasa_aceptacion': tasa_aceptacion,
        'tiempo_promedio_respuesta': tiempo_promedio_respuesta,
        'documentos': documentos,
    }
    
    return render(request, 'configuracion/institucion_detail.html', context)


@login_required
@require_operar_programa
def programa_derivaciones(request, institucion_programa_id):
    """Vista de derivaciones de un programa específico"""
    ip = request.institucion_programa
    
    # Filtros
    estado = request.GET.get('estado', '')
    
    derivaciones = DerivacionCiudadano.objects.filter(
        institucion_programa=ip
    ).select_related('ciudadano', 'derivado_por')

    if estado:
        derivaciones = derivaciones.filter(estado=estado)

    derivaciones = derivaciones.order_by('-creado')

    context = {
        'institucion_programa': ip,
        'derivaciones': derivaciones,
        'estados': EstadoDerivacionCiudadano.choices,
        'estado_filtro': estado,
    }
    
    return render(request, 'legajos/programa_derivaciones.html', context)


@login_required
@require_http_methods(["POST"])
def aceptar_derivacion(request, derivacion_id):
    """Acepta una derivación institucional"""
    derivacion = get_object_or_404(DerivacionCiudadano, id=derivacion_id)

    # Verificar permisos
    if not puede_operar_programa(derivacion.institucion_programa, request.user):
        messages.error(request, 'No tiene permisos para operar este programa.')
        return redirect('legajos:programas')

    try:
        caso, created = DerivacionCiudadanoService.aceptar_derivacion(
            derivacion_id=derivacion_id,
            usuario=request.user,
        )
        
        if created:
            messages.success(request, f'Derivación aceptada. Caso {caso.codigo} creado exitosamente.')
        else:
            messages.info(request, f'Derivación unificada con caso existente {caso.codigo}.')
        
        return redirect('legajos:programa_casos', institucion_programa_id=caso.institucion_programa.id)
        
    except ValidationError as e:
        messages.error(request, str(e))
        return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@require_http_methods(["GET", "POST"])
def rechazar_derivacion_view(request, derivacion_id):
    """Vista para rechazar derivación"""
    derivacion = get_object_or_404(DerivacionCiudadano, id=derivacion_id)

    # Verificar permisos
    if not puede_operar_programa(derivacion.institucion_programa, request.user):
        messages.error(request, 'No tiene permisos para operar este programa.')
        return redirect('legajos:programas')

    if request.method == 'POST':
        form = RechazarDerivacionForm(request.POST)
        if form.is_valid():
            try:
                DerivacionCiudadanoService.rechazar_derivacion(
                    derivacion_id=derivacion_id,
                    usuario=request.user,
                    motivo_rechazo=form.cleaned_data['motivo_rechazo'],
                )
                messages.success(request, 'Derivación rechazada exitosamente.')
                return redirect('legajos:programa_derivaciones', 
                              institucion_programa_id=derivacion.institucion_programa.id)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = RechazarDerivacionForm()
    
    context = {
        'derivacion': derivacion,
        'form': form,
    }
    
    return render(request, 'legajos/rechazar_derivacion.html', context)


@login_required
@require_operar_programa
def programa_casos(request, institucion_programa_id):
    """Vista de casos activos de un programa"""
    ip = request.institucion_programa
    
    # Filtros
    estado = request.GET.get('estado', '')
    
    casos = CasoInstitucional.objects.filter(
        institucion_programa=ip
    ).select_related('ciudadano', 'responsable')
    
    if estado:
        casos = casos.filter(estado=estado)
    else:
        # Por defecto mostrar solo activos y en seguimiento
        casos = casos.filter(estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO])
    
    casos = casos.order_by('-fecha_apertura')
    
    context = {
        'institucion_programa': ip,
        'casos': casos,
        'estados': EstadoCaso.choices,
        'estado_filtro': estado,
    }
    
    return render(request, 'legajos/programa_casos.html', context)


@login_required
def caso_detalle(request, caso_id):
    """Detalle de un caso institucional"""
    caso = get_object_or_404(
        CasoInstitucional.objects.select_related(
            'ciudadano',
            'institucion_programa__institucion',
            'institucion_programa__programa',
            'responsable',
            'derivacion_origen',
        ),
        id=caso_id
    )
    
    # Verificar permisos
    if not puede_ver_programa(caso.institucion_programa, request.user):
        messages.error(request, 'No tiene permisos para ver este caso.')
        return redirect('legajos:ciudadanos')
    
    # TODO: Historial de estados cuando exista HistorialEstadoCaso
    # historial = caso.historial_estados.select_related('usuario').order_by('-creado')
    historial = []
    
    context = {
        'caso': caso,
        'historial': historial,
        'puede_operar': puede_operar_programa(caso.institucion_programa, request.user),
    }
    
    return render(request, 'legajos/caso_detalle.html', context)


@login_required
@require_operar_programa
def cambiar_estado_caso_view(request, caso_id):
    """Vista para cambiar estado de caso"""
    caso = get_object_or_404(CasoInstitucional, id=caso_id)
    
    if request.method == 'POST':
        form = CambiarEstadoCasoForm(request.POST)
        if form.is_valid():
            try:
                CasoService.cambiar_estado_caso(
                    caso_id=caso_id,
                    nuevo_estado=form.cleaned_data['nuevo_estado'],
                    usuario=request.user,
                    observacion=form.cleaned_data.get('observacion', ''),
                    motivo_cierre=form.cleaned_data.get('motivo_cierre', '')
                )
                messages.success(request, 'Estado del caso actualizado exitosamente.')
                return redirect('legajos:caso_detalle', caso_id=caso_id)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = CambiarEstadoCasoForm(initial={'nuevo_estado': caso.estado})
    
    context = {
        'caso': caso,
        'form': form,
    }
    
    return render(request, 'legajos/cambiar_estado_caso.html', context)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@login_required
@require_http_methods(["GET"])
def api_programa_indicadores(request, institucion_programa_id):
    """API: Indicadores de un programa"""
    ip = get_object_or_404(InstitucionPrograma, id=institucion_programa_id)
    
    if not puede_ver_programa(ip, request.user):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    # Calcular indicadores
    total_derivaciones = ip.derivaciones.count()
    derivaciones_pendientes = ip.derivaciones.filter(estado=EstadoDerivacionCiudadano.PENDIENTE).count()
    derivaciones_aceptadas = ip.derivaciones.filter(estado=EstadoDerivacionCiudadano.ACEPTADA).count()
    
    total_casos = ip.casos.count()
    casos_activos = ip.casos.filter(estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO]).count()
    casos_egresados = ip.casos.filter(estado=EstadoCaso.EGRESADO).count()
    
    cupo_utilizado = casos_activos
    cupo_disponible = ip.cupo_disponible
    
    data = {
        'total_derivaciones': total_derivaciones,
        'derivaciones_pendientes': derivaciones_pendientes,
        'derivaciones_aceptadas': derivaciones_aceptadas,
        'total_casos': total_casos,
        'casos_activos': casos_activos,
        'casos_egresados': casos_egresados,
        'cupo_utilizado': cupo_utilizado,
        'cupo_maximo': ip.cupo_maximo,
        'cupo_disponible': cupo_disponible,
        'controla_cupo': ip.controlar_cupo,
    }
    
    return JsonResponse(data)
