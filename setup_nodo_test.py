"""
Script para configurar datos iniciales del Sistema NODO
Ejecutar: python manage.py shell < setup_nodo_test.py
"""

from django.contrib.auth.models import User
from core.models import Institucion
from legajos.models import LegajoInstitucional
from legajos.models_programas import Programa
from legajos.models_institucional import InstitucionPrograma, UsuarioInstitucionPrograma

print("=" * 80)
print("CONFIGURACIÓN INICIAL - SISTEMA NODO")
print("=" * 80)

# 1. Crear Programas
print("\n1. Creando Programas...")

programas_data = [
    {
        'codigo': 'SEDRONAR',
        'nombre': 'Acompañamiento SEDRONAR',
        'tipo': 'ACOMPANAMIENTO_SEDRONAR',
        'descripcion': 'Programa de acompañamiento integral SEDRONAR',
        'icono': 'support_agent',
        'color': '#6366f1',
        'orden': 1,
    },
    {
        'codigo': 'NACHEC',
        'nombre': 'ÑACHEC',
        'tipo': 'NACHEC',
        'descripcion': 'Programa ÑACHEC',
        'icono': 'school',
        'color': '#10b981',
        'orden': 2,
    },
    {
        'codigo': 'ECONOMICO',
        'nombre': 'Acompañamiento Económico',
        'tipo': 'ECONOMICO',
        'descripcion': 'Programa de acompañamiento económico',
        'icono': 'attach_money',
        'color': '#f59e0b',
        'orden': 3,
    },
]

programas_creados = []
for prog_data in programas_data:
    programa, created = Programa.objects.get_or_create(
        codigo=prog_data['codigo'],
        defaults=prog_data
    )
    if created:
        print(f"  ✓ Creado: {programa.nombre}")
    else:
        print(f"  → Ya existe: {programa.nombre}")
    programas_creados.append(programa)

# 2. Obtener institución de prueba
print("\n2. Obteniendo institución...")
try:
    institucion = Institucion.objects.get(id=1)
    print(f"  ✓ Institución: {institucion.nombre}")
except Institucion.DoesNotExist:
    print("  ✗ ERROR: No existe institución con ID=1")
    print("  → Crear una institución primero en /admin/")
    exit(1)

# 3. Crear/Verificar Legajo Institucional
print("\n3. Creando Legajo Institucional...")
user = User.objects.filter(is_superuser=True).first()
legajo, created = LegajoInstitucional.objects.get_or_create(
    institucion=institucion,
    defaults={
        'responsable_sedronar': user,
        'estado_global': 'ACTIVO'
    }
)
if created:
    print(f"  ✓ Legajo creado: {legajo.codigo}")
else:
    print(f"  → Legajo existente: {legajo.codigo}")
    # Asegurar que esté activo
    if legajo.estado_global != 'ACTIVO':
        legajo.estado_global = 'ACTIVO'
        legajo.save()
        print(f"  ✓ Estado actualizado a ACTIVO")

# 4. Habilitar programas en la institución
print("\n4. Habilitando programas en la institución...")
for programa in programas_creados:
    ip, created = InstitucionPrograma.objects.get_or_create(
        institucion=institucion,
        programa=programa,
        defaults={
            'estado_programa': 'ACTIVO',
            'activo': True,
            'cupo_maximo': 50,
            'controlar_cupo': False,
            'responsable_local': user,
        }
    )
    if created:
        print(f"  ✓ Habilitado: {programa.nombre}")
    else:
        print(f"  → Ya habilitado: {programa.nombre}")
        # Asegurar que esté activo
        if not ip.activo or ip.estado_programa != 'ACTIVO':
            ip.activo = True
            ip.estado_programa = 'ACTIVO'
            ip.save()
            print(f"    ✓ Actualizado a ACTIVO")

# 5. Asignar usuario a programas
print("\n5. Asignando permisos de usuario...")
programas_habilitados = InstitucionPrograma.objects.filter(
    institucion=institucion,
    activo=True
)

for ip in programas_habilitados:
    uip, created = UsuarioInstitucionPrograma.objects.get_or_create(
        usuario=user,
        institucion_programa=ip,
        defaults={
            'rol': 'RESPONSABLE_LOCAL',
            'activo': True
        }
    )
    if created:
        print(f"  ✓ Asignado a: {ip.programa.nombre}")
    else:
        print(f"  → Ya asignado a: {ip.programa.nombre}")

# 6. Resumen
print("\n" + "=" * 80)
print("CONFIGURACIÓN COMPLETADA")
print("=" * 80)
print(f"\n✓ Programas creados: {len(programas_creados)}")
print(f"✓ Institución: {institucion.nombre} (ID: {institucion.id})")
print(f"✓ Legajo institucional: {legajo.codigo}")
print(f"✓ Estado global: {legajo.estado_global}")
print(f"✓ Programas habilitados: {programas_habilitados.count()}")

print("\n" + "=" * 80)
print("ACCEDER A LA NUEVA VISTA:")
print("=" * 80)
print(f"\nURL: http://localhost:8001/legajos/instituciones/{institucion.id}/detalle-programatico/")
print("\nDeberías ver:")
print("  • Solapas estáticas: Resumen, Personal, Evaluaciones, Documentos")
print("  • Solapas dinámicas: Una por cada programa habilitado")
print("  • Badges con contadores en cada solapa de programa")
print("\n" + "=" * 80)
