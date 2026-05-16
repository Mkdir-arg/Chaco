from django.http import HttpResponseGone
from django.contrib.auth.decorators import login_required


@login_required
def derivar_programa_view(request, ciudadano_id):
    """DEPRECATED: flujo legacy removido junto con models_institucional."""
    return HttpResponseGone(
        'DEPRECATED: derivar_programa_view fue retirado tras la limpieza de SEDRONAR.'
    )
