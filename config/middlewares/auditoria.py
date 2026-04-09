from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from core.models_auditoria import LogAccion, SesionUsuario
from config.middlewares.threadlocals import get_current_user, get_current_request
import json


class AuditoriaMiddleware(MiddlewareMixin):
    """Middleware para capturar acciones de auditoría"""
    
    def process_request(self, request):
        # Actualizar última actividad de la sesión
        if request.user.is_authenticated and hasattr(request, 'session'):
            try:
                sesion = SesionUsuario.objects.get(
                    session_key=request.session.session_key,
                    activa=True
                )
                sesion.save()  # Actualiza ultima_actividad automáticamente
            except SesionUsuario.DoesNotExist:
                pass
        
        return None
    
    def process_response(self, request, response):
        # Log de acciones GET (vistas)
        if (request.method == 'GET' and 
            request.user.is_authenticated and 
            not request.path.startswith('/static/') and
            not request.path.startswith('/media/') and
            not request.path.startswith('/admin/jsi18n/') and
            response.status_code == 200):
            
            self._log_action(
                request=request,
                accion=LogAccion.TipoAccion.VIEW,
                detalles={'path': request.path, 'status_code': response.status_code}
            )
        
        return response
    
    def _log_action(self, request, accion, modelo=None, objeto_id=None, 
                   objeto_repr=None, detalles=None):
        """Crear log de acción"""
        try:
            LogAccion.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                accion=accion,
                modelo=modelo or '',
                objeto_id=str(objeto_id) if objeto_id else '',
                objeto_repr=objeto_repr or '',
                detalles=detalles or {},
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
        except Exception:
            # No fallar si hay error en auditoría
            pass
    
    def _get_client_ip(self, request):
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
    # Crear log de acción
    LogAccion.objects.create(
        usuario=user,
        accion=LogAccion.TipoAccion.LOGIN,
        detalles={'success': True},
        ip_address=_get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )
    
    # Asegurar que la sesión tenga una clave
    if not request.session.session_key:
        request.session.save()
    
    # Crear/actualizar sesión solo si tenemos session_key
    if request.session.session_key:
        SesionUsuario.objects.update_or_create(
            session_key=request.session.session_key,
            defaults={
                'usuario': user,
                'ip_address': _get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
                'activa': True,
                'fin_sesion': None
            }
        )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log de cierre de sesión"""
    if user:
        # Crear log de acción
        LogAccion.objects.create(
            usuario=user,
            accion=LogAccion.TipoAccion.LOGOUT,
            detalles={'success': True},
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        
        # Cerrar sesión
        if hasattr(request, 'session') and request.session.session_key:
            try:
                sesiones = SesionUsuario.objects.filter(
                    usuario=user,
                    activa=True
                )
                for sesion in sesiones:
                    sesion.activa = False
                    sesion.fin_sesion = timezone.now()
                    sesion.save()
            except Exception:
                pass


def _get_client_ip(request):
    """Obtener IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_model_action(accion, instance, usuario=None, detalles=None):
    """Función helper para log de acciones de modelo"""
    request = get_current_request()
    if not request:
        return
    
    usuario = usuario or get_current_user()
    if not usuario or not usuario.is_authenticated:
        return
    
    LogAccion.objects.create(
        usuario=usuario,
        accion=accion,
        modelo=instance._meta.label,
        objeto_id=str(instance.pk),
        objeto_repr=str(instance)[:200],
        detalles=detalles or {},
        ip_address=_get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )