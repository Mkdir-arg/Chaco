import time
import threading
import logging
from django.core.cache import cache
from django.http import HttpResponse

logger = logging.getLogger(__name__)

class ConcurrencyLimitMiddleware:
    """Middleware para controlar concurrencia y evitar sobrecarga"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.active_requests = threading.local()
        
    def __call__(self, request):
        try:
            current_load = cache.get('active_requests', 0)
            
            if current_load > 1500:
                logger.warning(f"Sistema sobrecargado: {current_load} requests activos")
                return HttpResponse(
                    "Sistema temporalmente sobrecargado. Intente en unos segundos.",
                    status=503
                )
            
            cache.set('active_requests', current_load + 1, 60)
            
            try:
                response = self.get_response(request)
            finally:
                try:
                    current_load = cache.get('active_requests', 1)
                    cache.set('active_requests', max(0, current_load - 1), 60)
                except Exception as e:
                    logger.error(f"Error decrementando contador: {e}")
            
            return response
        except Exception as e:
            logger.error(f"Error en ConcurrencyLimitMiddleware: {e}", exc_info=True)
            return self.get_response(request)

class RequestMetricsMiddleware:
    """Middleware para métricas de performance en tiempo real"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        start_time = time.time()
        
        try:
            response = self.get_response(request)
            response_time = time.time() - start_time
            
            try:
                metrics_key = f"metrics:{int(time.time() // 60)}"
                current_metrics = cache.get(metrics_key, {'count': 0, 'total_time': 0})
                current_metrics['count'] += 1
                current_metrics['total_time'] += response_time
                cache.set(metrics_key, current_metrics, 300)
            except Exception as e:
                logger.debug(f"Error guardando métricas: {e}")
            
            if hasattr(response, '__setitem__'):
                response['X-Response-Time'] = f"{response_time:.3f}s"
                try:
                    response['X-Active-Requests'] = str(cache.get('active_requests', 0))
                except:
                    pass
            
            return response
        except Exception as e:
            logger.error(f"Error en RequestMetricsMiddleware: {e}", exc_info=True)
            return self.get_response(request)