from functools import wraps
from django.http import HttpResponse
from .models_auditoria import LogDescargaArchivo
from config.middlewares.threadlocals import get_current_request


def log_descarga_archivo(func):
    """Decorator para loggear descargas de archivos"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        
        # Solo loggear si es una descarga exitosa
        if (isinstance(response, HttpResponse) and 
            response.status_code == 200 and
            'attachment' in response.get('Content-Disposition', '')):
            
            try:
                # Extraer nombre del archivo del Content-Disposition
                content_disp = response.get('Content-Disposition', '')
                filename = 'archivo_desconocido'
                if 'filename=' in content_disp:
                    filename = content_disp.split('filename=')[1].strip('"')
                
                # Crear log de descarga
                LogDescargaArchivo.objects.create(
                    usuario=request.user if request.user.is_authenticated else None,
                    archivo_nombre=filename,
                    archivo_path=request.path,
                    modelo_origen=kwargs.get('modelo', ''),
                    objeto_id=str(kwargs.get('pk', '')),
                    ip_address=_get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                )
            except Exception:
                # No fallar si hay error en auditoría
                pass
        
        return response
    return wrapper


def _get_client_ip(request):
    """Obtener IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip