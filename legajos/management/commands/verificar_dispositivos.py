from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from core.models import DispositivoRed, Provincia, Municipio, Localidad
from legajos.models import Ciudadano


class Command(BaseCommand):
    help = 'Verifica y crea datos básicos para el funcionamiento del sistema'

    def handle(self, *args, **options):
        self.stdout.write('Verificando configuración del sistema...')
        
        # Verificar dispositivos
        dispositivos_count = DispositivoRed.objects.filter(activo=True).count()
        self.stdout.write(f'Dispositivos activos: {dispositivos_count}')
        
        if dispositivos_count == 0:
            self.stdout.write('No hay dispositivos activos. Creando dispositivo de prueba...')
            self.crear_dispositivo_prueba()
        
        # Verificar grupos
        self.verificar_grupos()
        
        # Verificar ciudadanos
        ciudadanos_count = Ciudadano.objects.filter(activo=True).count()
        self.stdout.write(f'Ciudadanos activos: {ciudadanos_count}')
        
        if ciudadanos_count == 0:
            self.stdout.write('No hay ciudadanos activos. Creando ciudadano de prueba...')
            self.crear_ciudadano_prueba()
        
        self.stdout.write(self.style.SUCCESS('Verificación completada'))

    def crear_dispositivo_prueba(self):
        # Crear provincia si no existe
        provincia, created = Provincia.objects.get_or_create(
            nombre='Buenos Aires'
        )
        
        # Crear municipio si no existe
        municipio, created = Municipio.objects.get_or_create(
            nombre='La Plata',
            provincia=provincia
        )
        
        # Crear localidad si no existe
        localidad, created = Localidad.objects.get_or_create(
            nombre='La Plata',
            municipio=municipio
        )
        
        # Crear dispositivo
        dispositivo = DispositivoRed.objects.create(
            tipo='CAAC',
            nombre='CAAC La Plata',
            provincia=provincia,
            municipio=municipio,
            localidad=localidad,
            direccion='Calle Ejemplo 123',
            telefono='221-123-4567',
            email='caac.laplata@sedronar.gov.ar',
            activo=True,
            descripcion='Casa de Atención y Acompañamiento Comunitario de La Plata'
        )
        
        self.stdout.write(f'Dispositivo creado: {dispositivo.nombre}')

    def verificar_grupos(self):
        grupos_necesarios = ['Responsable', 'Ciudadanos', 'Administrador', 'EncargadoDispositivo']
        
        for grupo_nombre in grupos_necesarios:
            grupo, created = Group.objects.get_or_create(name=grupo_nombre)
            if created:
                self.stdout.write(f'Grupo creado: {grupo_nombre}')
            else:
                self.stdout.write(f'Grupo existente: {grupo_nombre}')

    def crear_ciudadano_prueba(self):
        ciudadano = Ciudadano.objects.create(
            dni='12345678',
            nombre='Juan',
            apellido='Pérez',
            fecha_nacimiento='1990-01-01',
            genero='M',
            telefono='11-1234-5678',
            email='juan.perez@example.com',
            domicilio='Calle Falsa 123',
            activo=True
        )
        
        self.stdout.write(f'Ciudadano creado: {ciudadano.nombre} {ciudadano.apellido}')