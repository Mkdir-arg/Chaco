from django import template
from legajos.models_programas import Programa

register = template.Library()


@register.simple_tag
def programas_activos():
    """Retorna todos los programas activos ordenados"""
    return Programa.objects.filter(estado='ACTIVO').order_by('orden', 'nombre')
