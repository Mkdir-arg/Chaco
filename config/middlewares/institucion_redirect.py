from django.shortcuts import redirect
from django.urls import reverse


class InstitucionRedirectMiddleware:
    """Middleware que restringe el acceso de usuarios EncargadoInstitucion solo a su institución"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs permitidas para usuarios EncargadoInstitucion
        self.allowed_paths = [
            '/logout',
            '/static/',
            '/media/',
            '/api/',
        ]
    
    def __call__(self, request):
        if request.user.is_authenticated and request.user.groups.filter(name='EncargadoInstitucion').exists():
            path = request.path
            
            # Permitir URLs específicas
            if any(path.startswith(allowed) for allowed in self.allowed_paths):
                return self.get_response(request)
            
            # Obtener la institución del usuario
            from core.models import Institucion
            institucion = Institucion.objects.filter(encargados=request.user).first()
            
            if institucion:
                institucion_url = reverse('configuracion:institucion_detalle', kwargs={'pk': institucion.pk})
                
                # Si ya está en una URL permitida de su institución, continuar
                if path.startswith('/configuracion/instituciones/') or path.startswith('/configuracion/actividades/'):
                    # Verificar que sea su institución
                    if f'/configuracion/instituciones/{institucion.pk}/' in path or self._es_actividad_propia(request, institucion):
                        return self.get_response(request)
                
                # Redirigir a su institución si intenta acceder a otra URL
                if path != institucion_url and path != '/':
                    return redirect(institucion_url)
        
        return self.get_response(request)
    
    def _es_actividad_propia(self, request, institucion):
        """Verifica si la actividad pertenece a la institución del usuario"""
        from legajos.models import LegajoInstitucional
        try:
            legajo = LegajoInstitucional.objects.filter(institucion=institucion).first()
            if legajo and '/configuracion/actividades/' in request.path:
                return True
        except:
            pass
        return False
