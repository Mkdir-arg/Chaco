from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def dashboard_contactos_simple(request):
    """Dashboard simple para probar"""
    return render(request, 'legajos/dashboard_simple.html', {
        'titulo': 'Dashboard de Contactos - Funcionando!'
    })

@login_required  
def test_api(request):
    """API de prueba"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Las APIs funcionan correctamente'
    })