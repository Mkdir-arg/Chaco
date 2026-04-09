from django.db import migrations


ESTADO_MAP = {
    'PENDIENTE': 'PENDIENTE',
    'ACEPTADA': 'ACEPTADA',
    'RECHAZADA': 'RECHAZADA',
    'ACEPTADA_UNIFICADA': 'ACEPTADA',
}


def copiar_derivaciones(apps, schema_editor):
    DerivacionInstitucional = apps.get_model('legajos', 'DerivacionInstitucional')
    DerivacionCiudadano = apps.get_model('legajos', 'DerivacionCiudadano')

    batch = []
    for d in DerivacionInstitucional.objects.all().iterator(chunk_size=200):
        batch.append(DerivacionCiudadano(
            ciudadano_id=d.ciudadano_id,
            tipo_inicio='DERIVACION',
            institucion_programa_id=d.institucion_programa_id,
            actividad_destino_id=None,
            programa_origen_id=None,
            institucion_id=d.institucion_id,
            programa_id=d.programa_id,
            estado=ESTADO_MAP.get(d.estado, 'PENDIENTE'),
            urgencia=d.urgencia,
            motivo=d.motivo,
            observaciones=d.observaciones,
            derivado_por_id=d.derivado_por_id,
            respuesta=d.respuesta,
            fecha_respuesta=d.fecha_respuesta,
            quien_responde_id=d.respondido_por_id,
            caso_creado_id=d.caso_creado_id,
        ))
        if len(batch) >= 200:
            DerivacionCiudadano.objects.bulk_create(batch)
            batch = []

    if batch:
        DerivacionCiudadano.objects.bulk_create(batch)


def revertir_copia(apps, schema_editor):
    DerivacionCiudadano = apps.get_model('legajos', 'DerivacionCiudadano')
    DerivacionCiudadano.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('legajos', '0026_derivacionciudadano'),
    ]

    operations = [
        migrations.RunPython(copiar_derivaciones, revertir_copia),
    ]
