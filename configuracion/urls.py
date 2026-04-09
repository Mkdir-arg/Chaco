from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .views import programas as views_programas

app_name = 'configuracion'

urlpatterns = [
    # Provincias
    path('provincias/', login_required(views.ProvinciaListView.as_view()), name='provincias'),
    path('provincias/crear/', login_required(views.ProvinciaCreateView.as_view()), name='provincia_crear'),
    path('provincias/<int:pk>/editar/', login_required(views.ProvinciaUpdateView.as_view()), name='provincia_editar'),
    path('provincias/<int:pk>/eliminar/', login_required(views.ProvinciaDeleteView.as_view()), name='provincia_eliminar'),
    
    # Municipios
    path('municipios/', login_required(views.MunicipioListView.as_view()), name='municipios'),
    path('municipios/crear/', login_required(views.MunicipioCreateView.as_view()), name='municipio_crear'),
    path('municipios/<int:pk>/editar/', login_required(views.MunicipioUpdateView.as_view()), name='municipio_editar'),
    path('municipios/<int:pk>/eliminar/', login_required(views.MunicipioDeleteView.as_view()), name='municipio_eliminar'),
    
    # Localidades
    path('localidades/', login_required(views.LocalidadListView.as_view()), name='localidades'),
    path('localidades/crear/', login_required(views.LocalidadCreateView.as_view()), name='localidad_crear'),
    path('localidades/<int:pk>/editar/', login_required(views.LocalidadUpdateView.as_view()), name='localidad_editar'),
    path('localidades/<int:pk>/eliminar/', login_required(views.LocalidadDeleteView.as_view()), name='localidad_eliminar'),
    
    # Instituciones
    path('instituciones/<int:pk>/', login_required(views.InstitucionDetailView.as_view()), name='institucion_detalle'),
    
    # Actividades
    path('actividades/<int:pk>/', login_required(views.ActividadDetailView.as_view()), name='actividad_detalle'),
    path('actividades/<int:actividad_pk>/staff/crear/', login_required(views.StaffActividadCreateView.as_view()), name='staff_crear'),
    path('actividades/<int:actividad_pk>/buscar-personal/', views.buscar_personal_ajax, name='buscar_personal_ajax'),
    path('derivaciones/<int:pk>/aceptar/', login_required(views.DerivacionAceptarView.as_view()), name='derivacion_aceptar'),
    path('derivaciones/<int:pk>/rechazar/', login_required(views.DerivacionRechazarView.as_view()), name='derivacion_rechazar'),
    path('inscriptos/<int:pk>/editar/', login_required(views.InscriptoEditarView.as_view()), name='inscripto_editar'),
    path('actividades/<int:pk>/editar/', login_required(views.ActividadEditarView.as_view()), name='actividad_editar'),
    path('staff/<int:pk>/editar/', login_required(views.StaffEditarView.as_view()), name='staff_editar'),
    path('staff/<int:pk>/desasignar/', login_required(views.StaffDesasignarView.as_view()), name='staff_desasignar'),
    path('actividades/<int:pk>/asistencia/', login_required(views.AsistenciaView.as_view()), name='asistencia'),
    path('actividades/<int:pk>/tomar-asistencia/', login_required(views.TomarAsistenciaView.as_view()), name='tomar_asistencia'),
    path('actividades/<int:actividad_pk>/inscribir/', login_required(views.InscripcionDirectaView.as_view()), name='inscripcion_directa'),
    path('actividades/<int:pk>/clases/', login_required(views.ClaseListView.as_view()), name='clase_lista'),
    path('actividades/<int:actividad_pk>/clases/crear/', login_required(views.ClaseCreateView.as_view()), name='clase_crear'),
    path('clases/<int:pk>/editar/', login_required(views.ClaseEditarView.as_view()), name='clase_editar'),
    path('clases/<int:pk>/eliminar/', login_required(views.ClaseEliminarView.as_view()), name='clase_eliminar'),
    path('clases/<int:pk>/asistencia/', login_required(views.ClaseAsistenciaView.as_view()), name='clase_asistencia'),
    
    # Gestión de legajo institucional
    path('instituciones/<int:institucion_pk>/personal/crear/', login_required(views.PersonalInstitucionCreateView.as_view()), name='personal_crear'),
    path('instituciones/<int:institucion_pk>/evaluaciones/crear/', login_required(views.EvaluacionInstitucionCreateView.as_view()), name='evaluacion_crear'),
    path('instituciones/<int:institucion_pk>/planes/crear/', login_required(views.PlanFortalecimientoCreateView.as_view()), name='plan_crear'),
    path('instituciones/<int:institucion_pk>/indicadores/crear/', login_required(views.IndicadorInstitucionCreateView.as_view()), name='indicador_crear'),
    path('instituciones/<int:pk>/documentos/subir/', login_required(views.documento_subir), name='documento_subir'),
    

    
    # Secretarías y Subsecretarías
    path('secretarias/', login_required(views.SecretariaListView.as_view()), name='secretarias'),
    path('secretarias/crear/', login_required(views.SecretariaCreateView.as_view()), name='secretaria_crear'),
    path('secretarias/<int:pk>/editar/', login_required(views.SecretariaUpdateView.as_view()), name='secretaria_editar'),
    path('secretarias/<int:pk>/eliminar/', login_required(views.SecretariaDeleteView.as_view()), name='secretaria_eliminar'),
    path('subsecretarias/', login_required(views.SubsecretariaListView.as_view()), name='subsecretarias'),
    path('subsecretarias/crear/', login_required(views.SubsecretariaCreateView.as_view()), name='subsecretaria_crear'),
    path('subsecretarias/<int:pk>/editar/', login_required(views.SubsecretariaUpdateView.as_view()), name='subsecretaria_editar'),
    path('subsecretarias/<int:pk>/eliminar/', login_required(views.SubsecretariaDeleteView.as_view()), name='subsecretaria_eliminar'),

    # Programas — wizard de configuración
    path('programas/', views_programas.programa_list, name='programas'),
    path('programas/nuevo/paso1/', views_programas.programa_wizard_paso1, name='programa_wizard_paso1'),
    path('programas/nuevo/paso2/', views_programas.programa_wizard_paso2, name='programa_wizard_paso2'),
    path('programas/nuevo/paso3/', views_programas.programa_wizard_paso3, name='programa_wizard_paso3'),
    path('programas/nuevo/paso4/', views_programas.programa_wizard_paso4, name='programa_wizard_paso4'),
    path('programas/<int:pk>/editar/paso1/', views_programas.programa_editar_paso1, name='programa_editar_paso1'),
    path('programas/<int:pk>/editar/paso2/', views_programas.programa_editar_paso2, name='programa_editar_paso2'),
    path('programas/<int:pk>/editar/paso3/', views_programas.programa_editar_paso3, name='programa_editar_paso3'),
    path('programas/<int:pk>/editar/paso4/', views_programas.programa_editar_paso4, name='programa_editar_paso4'),
    path('programas/<int:pk>/estado/', views_programas.programa_cambiar_estado, name='programa_cambiar_estado'),

    # Dispositivos (compatibilidad)
    path('dispositivos/', login_required(views.InstitucionListView.as_view()), name='dispositivos'),
    path('dispositivos/crear/', login_required(views.InstitucionCreateView.as_view()), name='dispositivo_crear'),
    path('dispositivos/<int:pk>/editar/', login_required(views.InstitucionUpdateView.as_view()), name='dispositivo_editar'),
    path('dispositivos/<int:pk>/eliminar/', login_required(views.InstitucionDeleteView.as_view()), name='dispositivo_eliminar'),
]