from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.contrib.auth.models import User
from ..models import LegajoAtencion, Ciudadano
from ..models_contactos import (
    VinculoFamiliar, ProfesionalTratante, DispositivoVinculado, 
    ContactoEmergencia
)
from core.models import DispositivoRed


@login_required
def red_contactos_view(request, legajo_id):
    """Vista principal de la red de contactos"""
    legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
    return render(request, 'legajos/red_contactos.html', {
        'legajo': legajo
    })


@login_required
def vinculos_api(request, legajo_id):
    """API para obtener vínculos familiares"""
    legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
    
    vinculos = VinculoFamiliar.objects.filter(
        ciudadano_principal=legajo.ciudadano,
        activo=True
    ).select_related('ciudadano_vinculado')
    
    data = []
    for vinculo in vinculos:
        data.append({
            'id': vinculo.id,
            'ciudadano_vinculado': {
                'id': vinculo.ciudadano_vinculado.id,
                'nombre': vinculo.ciudadano_vinculado.nombre,
                'apellido': vinculo.ciudadano_vinculado.apellido,
                'dni': vinculo.ciudadano_vinculado.dni,
                'telefono': vinculo.ciudadano_vinculado.telefono
            },
            'tipo_vinculo': vinculo.tipo_vinculo,
            'tipo_vinculo_display': vinculo.get_tipo_vinculo_display(),
            'es_contacto_emergencia': vinculo.es_contacto_emergencia,
            'es_referente_tratamiento': vinculo.es_referente_tratamiento,
            'convive': vinculo.convive,
            'telefono_alternativo': vinculo.telefono_alternativo,
            'observaciones': vinculo.observaciones
        })
    
    return JsonResponse({'vinculos': data})


@login_required
def profesionales_api(request, legajo_id):
    """API para obtener profesionales tratantes"""
    legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
    
    profesionales = ProfesionalTratante.objects.filter(
        legajo=legajo,
        activo=True
    ).select_related('usuario', 'dispositivo')
    
    data = []
    for prof in profesionales:
        data.append({
            'id': prof.id,
            'usuario': {
                'id': prof.usuario.id,
                'nombre': prof.usuario.get_full_name() or prof.usuario.username,
                'email': prof.usuario.email
            },
            'rol': prof.rol,
            'rol_display': prof.get_rol_display(),
            'es_responsable_principal': prof.es_responsable_principal,
            'dispositivo': {
                'id': prof.dispositivo.id,
                'nombre': prof.dispositivo.nombre,
                'tipo': prof.dispositivo.get_tipo_display()
            },
            'fecha_asignacion': prof.fecha_asignacion.isoformat(),
            'observaciones': prof.observaciones
        })
    
    return JsonResponse({'profesionales': data})


@login_required
def dispositivos_api(request, legajo_id):
    """API para obtener dispositivos vinculados"""
    legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
    
    dispositivos = DispositivoVinculado.objects.filter(
        legajo=legajo
    ).select_related('dispositivo', 'referente_dispositivo')
    
    data = []
    for disp in dispositivos:
        data.append({
            'id': disp.id,
            'dispositivo': {
                'id': disp.dispositivo.id,
                'nombre': disp.dispositivo.nombre,
                'tipo': disp.dispositivo.get_tipo_display(),
                'direccion': disp.dispositivo.direccion
            },
            'fecha_admision': disp.fecha_admision.isoformat(),
            'fecha_egreso': disp.fecha_egreso.isoformat() if disp.fecha_egreso else None,
            'estado': disp.estado,
            'estado_display': disp.get_estado_display(),
            'referente': disp.referente_dispositivo.get_full_name() if disp.referente_dispositivo else None,
            'observaciones': disp.observaciones
        })
    
    return JsonResponse({'dispositivos': data})


@login_required
def emergencias_api(request, legajo_id):
    """API para obtener contactos de emergencia"""
    legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
    
    contactos = ContactoEmergencia.objects.filter(
        legajo=legajo,
        activo=True
    ).order_by('prioridad')
    
    data = []
    for contacto in contactos:
        data.append({
            'id': contacto.id,
            'nombre': contacto.nombre,
            'relacion': contacto.relacion,
            'telefono_principal': contacto.telefono_principal,
            'telefono_alternativo': contacto.telefono_alternativo,
            'email': contacto.email,
            'disponibilidad_24hs': contacto.disponibilidad_24hs,
            'prioridad': contacto.prioridad,
            'instrucciones_especiales': contacto.instrucciones_especiales
        })
    
    return JsonResponse({'contactos_emergencia': data})


@login_required
def buscar_ciudadanos_api(request):
    """API para buscar ciudadanos para vincular"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'ciudadanos': []})
    
    ciudadanos = Ciudadano.objects.filter(
        Q(nombre__icontains=query) | 
        Q(apellido__icontains=query) |
        Q(dni__icontains=query)
    )[:10]
    
    data = []
    for ciudadano in ciudadanos:
        data.append({
            'id': ciudadano.id,
            'nombre': ciudadano.nombre,
            'apellido': ciudadano.apellido,
            'dni': ciudadano.dni,
            'telefono': ciudadano.telefono,
            'nombre_completo': f"{ciudadano.apellido}, {ciudadano.nombre}"
        })
    
    return JsonResponse({'ciudadanos': data})


@login_required
def buscar_usuarios_api(request):
    """API para buscar usuarios para asignar como profesionales"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'usuarios': []})
    
    usuarios = User.objects.filter(
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) |
        Q(username__icontains=query),
        is_active=True
    )[:10]
    
    data = []
    for usuario in usuarios:
        data.append({
            'id': usuario.id,
            'username': usuario.username,
            'nombre_completo': usuario.get_full_name() or usuario.username,
            'email': usuario.email
        })
    
    return JsonResponse({'usuarios': data})


@login_required
@require_http_methods(["POST"])
def crear_vinculo(request, legajo_id):
    """Crear nuevo vínculo familiar"""
    legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
    
    try:
        ciudadano_vinculado_id = request.POST.get('ciudadano_vinculado')
        tipo_vinculo = request.POST.get('tipo_vinculo')
        
        ciudadano_vinculado = get_object_or_404(Ciudadano, id=ciudadano_vinculado_id)
        
        vinculo = VinculoFamiliar.objects.create(
            ciudadano_principal=legajo.ciudadano,
            ciudadano_vinculado=ciudadano_vinculado,
            tipo_vinculo=tipo_vinculo,
            es_contacto_emergencia=request.POST.get('es_contacto_emergencia') == 'on',
            es_referente_tratamiento=request.POST.get('es_referente_tratamiento') == 'on',
            convive=request.POST.get('convive') == 'on',
            telefono_alternativo=request.POST.get('telefono_alternativo', ''),
            observaciones=request.POST.get('observaciones', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Vínculo creado exitosamente',
            'vinculo_id': vinculo.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["POST"])
def crear_profesional(request, legajo_id):
    """Asignar profesional tratante"""
    legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
    
    try:
        usuario_id = request.POST.get('usuario')
        rol = request.POST.get('rol')
        dispositivo_id = request.POST.get('dispositivo')
        
        usuario = get_object_or_404(User, id=usuario_id)
        dispositivo = get_object_or_404(DispositivoRed, id=dispositivo_id)
        
        profesional = ProfesionalTratante.objects.create(
            legajo=legajo,
            usuario=usuario,
            rol=rol,
            dispositivo=dispositivo,
            es_responsable_principal=request.POST.get('es_responsable_principal') == 'on',
            observaciones=request.POST.get('observaciones', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Profesional asignado exitosamente',
            'profesional_id': profesional.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["POST"])
def crear_contacto_emergencia(request, legajo_id):
    """Crear contacto de emergencia"""
    legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
    
    try:
        contacto = ContactoEmergencia.objects.create(
            legajo=legajo,
            nombre=request.POST.get('nombre'),
            relacion=request.POST.get('relacion'),
            telefono_principal=request.POST.get('telefono_principal'),
            telefono_alternativo=request.POST.get('telefono_alternativo', ''),
            email=request.POST.get('email', ''),
            disponibilidad_24hs=request.POST.get('disponibilidad_24hs') == 'on',
            prioridad=int(request.POST.get('prioridad', 1)),
            instrucciones_especiales=request.POST.get('instrucciones_especiales', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Contacto de emergencia creado exitosamente',
            'contacto_id': contacto.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
