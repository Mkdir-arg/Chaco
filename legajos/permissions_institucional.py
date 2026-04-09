"""
Sistema de permisos contextuales para gestión programática institucional
"""
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from functools import wraps

from .models_institucional import InstitucionPrograma


def puede_ver_programa(institucion_programa, user):
    """
    Verifica si un usuario puede ver la solapa de un programa.

    Pueden ver: superusuarios, usuarios con grupo programaOperar,
    encargados de la institución y responsables locales del InstitucionPrograma.
    """
    if user.is_superuser:
        return True
    if user.groups.filter(name='programaOperar').exists():
        return True
    if institucion_programa.institucion.encargados.filter(id=user.id).exists():
        return True
    if institucion_programa.responsable_local_id == user.id:
        return True
    return False


def puede_operar_programa(institucion_programa, user):
    """
    Verifica si un usuario puede operar un programa (aceptar/rechazar derivaciones,
    modificar casos).

    Pueden operar: superusuarios, usuarios con grupo programaOperar,
    responsable local del InstitucionPrograma y coordinadores activos del programa.
    """
    if user.is_superuser:
        return True
    if user.groups.filter(name='programaOperar').exists():
        return True
    if institucion_programa.responsable_local_id == user.id:
        return True
    from .models_institucional import CoordinadorPrograma
    if CoordinadorPrograma.objects.filter(
        usuario=user,
        programa=institucion_programa.programa,
        activo=True,
    ).exists():
        return True
    return False


def puede_gestionar_programa(institucion_programa, user):
    """
    Verifica si un usuario puede gestionar un programa (cambiar estado, cupo, etc).

    Pueden gestionar: superusuarios y coordinadores activos del programa.
    """
    if user.is_superuser:
        return True
    from .models_institucional import CoordinadorPrograma
    if CoordinadorPrograma.objects.filter(
        usuario=user,
        programa=institucion_programa.programa,
        activo=True,
    ).exists():
        return True
    return False


def puede_ver_institucion(institucion, user):
    """
    Verifica si un usuario puede ver el detalle de una institución.
    
    Pueden ver:
    - SuperAdmin
    - Encargados de la institución
    - Usuarios asignados a algún programa de la institución
    
    Args:
        institucion: Instancia de Institucion
        user: Usuario a verificar
    
    Returns:
        bool: True si puede ver
    """
    if user.is_superuser:
        return True
    
    # Encargado de la institución
    if institucion.encargados.filter(id=user.id).exists():
        return True
    
    # TODO: Implementar UsuarioInstitucionPrograma
    # Asignado a algún programa de la institución
    # return UsuarioInstitucionPrograma.objects.filter(
    #     usuario=user,
    #     institucion_programa__institucion=institucion,
    #     activo=True
    # ).exists()
    return False


# ============================================================================
# DECORADORES
# ============================================================================

def require_ver_programa(view_func):
    """
    Decorador que requiere permiso para ver un programa.
    Espera institucion_programa_id en kwargs.
    """
    @wraps(view_func)
    def wrapper(request, institucion_programa_id, *args, **kwargs):
        ip = get_object_or_404(InstitucionPrograma, id=institucion_programa_id)
        
        if not puede_ver_programa(ip, request.user):
            raise PermissionDenied("No tiene permisos para ver este programa")
        
        # Agregar al request para evitar re-consultas
        request.institucion_programa = ip
        
        return view_func(request, institucion_programa_id, *args, **kwargs)
    
    return wrapper


def require_operar_programa(view_func):
    """
    Decorador que requiere permiso para operar un programa.
    Espera institucion_programa_id en kwargs.
    """
    @wraps(view_func)
    def wrapper(request, institucion_programa_id, *args, **kwargs):
        ip = get_object_or_404(InstitucionPrograma, id=institucion_programa_id)
        
        if not puede_operar_programa(ip, request.user):
            raise PermissionDenied("No tiene permisos para operar este programa")
        
        request.institucion_programa = ip
        
        return view_func(request, institucion_programa_id, *args, **kwargs)
    
    return wrapper


def require_gestionar_programa(view_func):
    """
    Decorador que requiere permiso para gestionar un programa.
    Espera institucion_programa_id en kwargs.
    """
    @wraps(view_func)
    def wrapper(request, institucion_programa_id, *args, **kwargs):
        ip = get_object_or_404(InstitucionPrograma, id=institucion_programa_id)
        
        if not puede_gestionar_programa(ip, request.user):
            raise PermissionDenied("No tiene permisos para gestionar este programa")
        
        request.institucion_programa = ip
        
        return view_func(request, institucion_programa_id, *args, **kwargs)
    
    return wrapper


def require_ver_institucion(view_func):
    """
    Decorador que requiere permiso para ver una institución.
    Espera institucion_id o pk en kwargs.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from core.models import Institucion
        
        institucion_id = kwargs.get('institucion_id') or kwargs.get('pk')
        institucion = get_object_or_404(Institucion, id=institucion_id)
        
        if not puede_ver_institucion(institucion, request.user):
            raise PermissionDenied("No tiene permisos para ver esta institución")
        
        request.institucion = institucion
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


# ============================================================================
# MIXINS PARA CLASS-BASED VIEWS
# ============================================================================

class VerProgramaMixin:
    """Mixin para vistas que requieren permiso de ver programa"""
    
    def dispatch(self, request, *args, **kwargs):
        institucion_programa_id = kwargs.get('institucion_programa_id')
        self.institucion_programa = get_object_or_404(InstitucionPrograma, id=institucion_programa_id)
        
        if not puede_ver_programa(self.institucion_programa, request.user):
            raise PermissionDenied("No tiene permisos para ver este programa")
        
        return super().dispatch(request, *args, **kwargs)


class OperarProgramaMixin:
    """Mixin para vistas que requieren permiso de operar programa"""
    
    def dispatch(self, request, *args, **kwargs):
        institucion_programa_id = kwargs.get('institucion_programa_id')
        self.institucion_programa = get_object_or_404(InstitucionPrograma, id=institucion_programa_id)
        
        if not puede_operar_programa(self.institucion_programa, request.user):
            raise PermissionDenied("No tiene permisos para operar este programa")
        
        return super().dispatch(request, *args, **kwargs)


class GestionarProgramaMixin:
    """Mixin para vistas que requieren permiso de gestionar programa"""
    
    def dispatch(self, request, *args, **kwargs):
        institucion_programa_id = kwargs.get('institucion_programa_id')
        self.institucion_programa = get_object_or_404(InstitucionPrograma, id=institucion_programa_id)
        
        if not puede_gestionar_programa(self.institucion_programa, request.user):
            raise PermissionDenied("No tiene permisos para gestionar este programa")
        
        return super().dispatch(request, *args, **kwargs)


class VerInstitucionMixin:
    """Mixin para vistas que requieren permiso de ver institución"""
    
    def dispatch(self, request, *args, **kwargs):
        from core.models import Institucion
        
        institucion_id = kwargs.get('institucion_id') or kwargs.get('pk')
        self.institucion = get_object_or_404(Institucion, id=institucion_id)
        
        if not puede_ver_institucion(self.institucion, request.user):
            raise PermissionDenied("No tiene permisos para ver esta institución")
        
        return super().dispatch(request, *args, **kwargs)
