from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from legajos.models_contactos import (
    HistorialContacto, VinculoFamiliar, ProfesionalTratante,
    DispositivoVinculado, ContactoEmergencia
)


class Command(BaseCommand):
    help = 'Configura grupos y permisos para el sistema de contactos'

    def handle(self, *args, **options):
        # Crear grupos de roles profesionales
        roles = [
            'Psicologo',
            'Psiquiatra', 
            'Medico',
            'Trabajador Social',
            'Operador Socioterapeutico',
            'Coordinador',
            'Director',
            'Enfermero',
            'Terapista Ocupacional',
            'Abogado'
        ]
        
        for rol in roles:
            group, created = Group.objects.get_or_create(name=rol)
            if created:
                self.stdout.write(f'Grupo creado: {rol}')
            else:
                self.stdout.write(f'Grupo existente: {rol}')
        
        # Configurar permisos por modelo
        modelos_contactos = [
            HistorialContacto,
            VinculoFamiliar, 
            ProfesionalTratante,
            DispositivoVinculado,
            ContactoEmergencia
        ]
        
        # Permisos básicos para todos los profesionales
        permisos_basicos = ['view', 'add', 'change']
        
        for modelo in modelos_contactos:
            content_type = ContentType.objects.get_for_model(modelo)
            
            for permiso in permisos_basicos:
                perm_codename = f'{permiso}_{modelo._meta.model_name}'
                try:
                    permission = Permission.objects.get(
                        codename=perm_codename,
                        content_type=content_type
                    )
                    
                    # Asignar a grupos específicos
                    grupos_con_acceso = [
                        'Coordinador', 'Director', 'Psicologo', 
                        'Trabajador Social', 'Operador Socioterapeutico'
                    ]
                    
                    for grupo_nombre in grupos_con_acceso:
                        grupo = Group.objects.get(name=grupo_nombre)
                        grupo.permissions.add(permission)
                        
                except Permission.DoesNotExist:
                    self.stdout.write(f'Permiso no encontrado: {perm_codename}')
        
        # Permisos especiales para coordinadores y directores
        permisos_delete = Permission.objects.filter(
            codename__startswith='delete_',
            content_type__in=[ContentType.objects.get_for_model(m) for m in modelos_contactos]
        )
        
        for grupo_nombre in ['Coordinador', 'Director']:
            grupo = Group.objects.get(name=grupo_nombre)
            for permiso in permisos_delete:
                grupo.permissions.add(permiso)
        
        self.stdout.write(
            self.style.SUCCESS('Configuración de roles y permisos completada')
        )