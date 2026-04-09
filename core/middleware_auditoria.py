"""
Middleware de Auditoría
Sistema SEDRONAR - Captura información de requests para auditoría
"""

from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from core.signals_auditoria import set_current_request
from core.models_auditoria import LogAccion, SesionUsuario
from core.models_auditoria_extendida import AuditoriaAccesoSensible
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, time


class AuditoriaMiddleware(MiddlewareMixin):
    """
    Middleware que captura información de la request y la hace disponible
    para los signals de auditoría
    """
    
    def process_request(self, request):
        """Guarda la request en thread local para acceso en signals"""
        set_current_request(request)
        return None
    
    def process_response(self, request, response):
        """Limpia la request del thread local"""
        set_current_request(None)
        return response


class AccesoSensibleMiddleware(MiddlewareMixin):
    """
    Middleware que audita accesos a vistas con datos sensibles
    """
    
    # Vistas que contienen datos sensibles
    VISTAS_SENSIBLES = [
        'legajos:detalle',
        'legajos:ciudadano_detalle',
        'legajos:evaluacion_detalle',
        'legajos:evento_critico_detalle',
        'legajos:consentimiento_detalle',
    ]
    
    # Patrones de URL sensibles
    PATRONES_SENSIBLES = [
        '/legajos/ciudadano/',
        '/legajos/legajo/',
        '/legajos/evaluacion/',
        '/legajos/evento/',
        '/legajos/consentimiento/',
    ]
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Audita el acceso a vistas sensibles
        """
        # Solo auditar usuarios autenticados
        if not request.user.is_authenticated:
            return None
        
        # Verificar si es una vista sensible
        es_sensible = False
        
        # Verificar por nombre de vista
        if hasattr(view_func, '__name__'):
            for vista in self.VISTAS_SENSIBLES:
                if vista in str(view_func.__name__):
                    es_sensible = True
                    break
        
        # Verificar por patrón de URL
        if not es_sensible:
            for patron in self.PATRONES_SENSIBLES:
                if patron in request.path:
                    es_sensible = True
                    break
        
        # Si es sensible y es GET (visualización), auditar
        if es_sensible and request.method == 'GET':
            self._auditar_acceso(request, view_kwargs)
        
        return None
    
    def _auditar_acceso(self, request, view_kwargs):
        """
        Crea un registro de auditoría de acceso sensible
        """
        try:
            # Determinar el objeto accedido
            object_id = view_kwargs.get('pk') or view_kwargs.get('id')
            if not object_id:
                return
            
            # Determinar el tipo de contenido
            content_type = self._determinar_content_type(request.path)
            if not content_type:
                return
            
            # Verificar si es fuera de horario
            fuera_horario = self._es_fuera_horario()
            
            # Verificar accesos múltiples
            acceso_multiple = self._verificar_acceso_multiple(
                request.user,
                content_type,
                object_id
            )
            
            # Crear registro de auditoría
            AuditoriaAccesoSensible.objects.create(
                content_type=content_type,
                object_id=str(object_id),
                usuario=request.user,
                tipo_acceso='VIEW',
                campos_accedidos=['all'],  # TODO: Especificar campos específicos
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                url_acceso=request.path,
                metodo_http=request.method,
                justificacion=request.GET.get('justificacion', ''),
                fuera_horario=fuera_horario,
                acceso_multiple=acceso_multiple
            )
            
            # Si es fuera de horario o acceso múltiple, generar alerta
            if fuera_horario or acceso_multiple:
                self._generar_alerta_acceso(request, fuera_horario, acceso_multiple)
        
        except Exception as e:
            # No interrumpir el flujo si falla la auditoría
            print(f"Error en auditoría de acceso: {e}")
    
    def _determinar_content_type(self, path):
        """Determina el ContentType basado en la URL"""
        try:
            if '/ciudadano/' in path:
                return ContentType.objects.get(app_label='legajos', model='ciudadano')
            elif '/legajo/' in path:
                return ContentType.objects.get(app_label='legajos', model='legajoatencion')
            elif '/evaluacion/' in path:
                return ContentType.objects.get(app_label='legajos', model='evaluacioninicial')
            elif '/evento/' in path:
                return ContentType.objects.get(app_label='legajos', model='eventocritico')
            elif '/consentimiento/' in path:
                return ContentType.objects.get(app_label='legajos', model='consentimiento')
        except ContentType.DoesNotExist:
            pass
        return None
    
    def _get_client_ip(self, request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _es_fuera_horario(self):
        """Verifica si es fuera del horario laboral (22:00-06:00)"""
        hora_actual = datetime.now().time()
        return hora_actual >= time(22, 0) or hora_actual < time(6, 0)
    
    def _verificar_acceso_multiple(self, usuario, content_type, object_id):
        """
        Verifica si hay múltiples accesos en corto tiempo (5 minutos)
        """
        from django.utils import timezone
        from datetime import timedelta
        
        hace_5_minutos = timezone.now() - timedelta(minutes=5)
        
        accesos_recientes = AuditoriaAccesoSensible.objects.filter(
            usuario=usuario,
            content_type=content_type,
            object_id=str(object_id),
            timestamp__gte=hace_5_minutos
        ).count()
        
        return accesos_recientes >= 3
    
    def _generar_alerta_acceso(self, request, fuera_horario, acceso_multiple):
        """Genera alerta de auditoría por acceso sospechoso"""
        from core.models_auditoria import AlertaAuditoria
        
        tipo_alerta = 'ACCESO_FUERA_HORARIO' if fuera_horario else 'ACTIVIDAD_SOSPECHOSA'
        severidad = 'ALTA' if fuera_horario else 'MEDIA'
        
        descripcion = ''
        if fuera_horario:
            descripcion = f'Acceso a datos sensibles fuera de horario laboral'
        if acceso_multiple:
            descripcion = f'Múltiples accesos a datos sensibles en corto tiempo'
        
        AlertaAuditoria.objects.create(
            tipo=tipo_alerta,
            severidad=severidad,
            usuario_afectado=request.user,
            descripcion=descripcion,
            detalles={
                'url': request.path,
                'ip': self._get_client_ip(request),
                'hora': datetime.now().isoformat(),
            }
        )


class DescargaArchivoMiddleware(MiddlewareMixin):
    """
    Middleware que audita descargas de archivos
    """
    
    # Patrones de URL de descarga
    PATRONES_DESCARGA = [
        '/media/',
        '/download/',
        '/export/',
    ]
    
    def process_response(self, request, response):
        """
        Audita descargas de archivos
        """
        # Solo auditar usuarios autenticados
        if not request.user.is_authenticated:
            return response
        
        # Verificar si es una descarga
        es_descarga = False
        for patron in self.PATRONES_DESCARGA:
            if patron in request.path:
                es_descarga = True
                break
        
        # También verificar por Content-Disposition header
        if not es_descarga and 'Content-Disposition' in response:
            es_descarga = True
        
        if es_descarga:
            self._auditar_descarga(request, response)
        
        return response
    
    def _auditar_descarga(self, request, response):
        """Crea un registro de auditoría de descarga"""
        from core.models_auditoria import LogDescargaArchivo
        
        try:
            # Extraer nombre del archivo
            archivo_nombre = self._extraer_nombre_archivo(request, response)
            
            LogDescargaArchivo.objects.create(
                usuario=request.user,
                archivo_nombre=archivo_nombre,
                archivo_path=request.path,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Verificar descarga masiva
            self._verificar_descarga_masiva(request.user)
        
        except Exception as e:
            print(f"Error en auditoría de descarga: {e}")
    
    def _extraer_nombre_archivo(self, request, response):
        """Extrae el nombre del archivo de la URL o headers"""
        # Intentar desde Content-Disposition
        if 'Content-Disposition' in response:
            disposition = response['Content-Disposition']
            if 'filename=' in disposition:
                return disposition.split('filename=')[1].strip('"')
        
        # Intentar desde la URL
        return request.path.split('/')[-1]
    
    def _get_client_ip(self, request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _verificar_descarga_masiva(self, usuario):
        """Verifica si hay descarga masiva (10+ en 5 minutos)"""
        from django.utils import timezone
        from datetime import timedelta
        from core.models_auditoria import LogDescargaArchivo, AlertaAuditoria
        
        hace_5_minutos = timezone.now() - timedelta(minutes=5)
        
        descargas_recientes = LogDescargaArchivo.objects.filter(
            usuario=usuario,
            timestamp__gte=hace_5_minutos
        ).count()
        
        if descargas_recientes >= 10:
            # Generar alerta
            AlertaAuditoria.objects.create(
                tipo='DESCARGA_MASIVA',
                severidad='ALTA',
                usuario_afectado=usuario,
                descripcion=f'Descarga masiva de archivos detectada ({descargas_recientes} descargas en 5 minutos)',
                detalles={
                    'cantidad_descargas': descargas_recientes,
                    'periodo': '5 minutos',
                }
            )


class SesionUsuarioMiddleware(MiddlewareMixin):
    """
    Middleware que trackea sesiones de usuario
    """
    
    def process_request(self, request):
        """Actualiza la última actividad de la sesión"""
        if request.user.is_authenticated and hasattr(request, 'session'):
            self._actualizar_sesion(request)
        return None
    
    def _actualizar_sesion(self, request):
        """Actualiza la última actividad de la sesión"""
        from core.models_auditoria import SesionUsuario
        from django.utils import timezone
        
        try:
            session_key = request.session.session_key
            if not session_key:
                return
            
            SesionUsuario.objects.filter(
                session_key=session_key,
                activa=True
            ).update(ultima_actividad=timezone.now())
        
        except Exception as e:
            print(f"Error actualizando sesión: {e}")
    
    def _get_client_ip(self, request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


def _get_client_ip(request):
    """Obtener IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log de inicio de sesión"""
    LogAccion.objects.create(
        usuario=user,
        accion=LogAccion.TipoAccion.LOGIN,
        detalles={'success': True},
        ip_address=_get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )
    
    if not request.session.session_key:
        request.session.save()
    
    if request.session.session_key:
        SesionUsuario.objects.filter(session_key=request.session.session_key).delete()
        SesionUsuario.objects.create(
            session_key=request.session.session_key,
            usuario=user,
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            activa=True
        )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log de cierre de sesión"""
    if user:
        LogAccion.objects.create(
            usuario=user,
            accion=LogAccion.TipoAccion.LOGOUT,
            detalles={'success': True},
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        
        if hasattr(request, 'session') and request.session.session_key:
            try:
                SesionUsuario.objects.filter(
                    session_key=request.session.session_key,
                    activa=True
                ).update(
                    activa=False,
                    fin_sesion=timezone.now()
                )
            except Exception:
                pass
