#!/usr/bin/env python
"""
Entrypoint para el contenedor Django
Ejecuta la configuración completa del sistema y luego inicia el servidor
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def wait_for_db():
    """Espera a que la base de datos esté disponible"""
    print("🔄 Esperando conexión a la base de datos...")
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            # Intentar conectar usando el cliente MySQL
            result = subprocess.run([
                'mysql', 
                '-h', os.environ.get('DATABASE_HOST', 'sedronar-mysql'),
                '-P', os.environ.get('DATABASE_PORT', '3306'),
                '-u', os.environ.get('DATABASE_USER', 'root'),
                f'-p{os.environ.get("DATABASE_PASSWORD", "sedronar123")}',
                '-e', 'SELECT 1'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Base de datos disponible!")
                return True
                
        except Exception as e:
            pass
            
        attempt += 1
        print(f"⏳ Intento {attempt}/{max_attempts} - Reintentando en 2 segundos...")
        time.sleep(2)
    
    print("❌ No se pudo conectar a la base de datos")
    return False

def run_setup():
    """Ejecuta el script de configuración completa"""
    print("\n🚀 Ejecutando configuración completa del sistema...")
    
    try:
        # Cambiar al directorio del proyecto
        os.chdir('/sisoc')
        
        # Ejecutar el script de configuración
        result = subprocess.run([
            sys.executable, 'setup_sistema_completo.py'
        ], check=True)
        
        print("✅ Configuración completada exitosamente!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en la configuración: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def start_server():
    """Inicia el servidor Django"""
    print("\n🌐 Iniciando servidor Django...")
    
    try:
        # Ejecutar el servidor Django
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        sys.exit(1)

def main():
    """Función principal del entrypoint"""
    print("=" * 60)
    print("🐳 SISOC - ENTRYPOINT DOCKER")
    print("=" * 60)
    
    # Esperar a que la base de datos esté disponible
    if not wait_for_db():
        sys.exit(1)
    
    # Ejecutar configuración completa
    if not run_setup():
        print("⚠️  Configuración falló, pero continuando con el servidor...")
    
    # Iniciar servidor
    start_server()

if __name__ == '__main__':
    main()