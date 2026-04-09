#!/usr/bin/env python
"""
Entrypoint simple para el contenedor Django
Ejecuta la configuración y luego inicia el servidor
"""

import os
import sys
import time
import subprocess

def wait_for_db():
    """Espera a que la base de datos esté disponible usando mysql client"""
    print("🔄 Esperando conexión a la base de datos...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
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
                
        except Exception:
            pass
            
        print(f"⏳ Intento {attempt + 1}/{max_attempts} - Reintentando en 2 segundos...")
        time.sleep(2)
    
    print("❌ No se pudo conectar a la base de datos")
    return False

def run_setup():
    """Ejecuta el script de configuración completa"""
    print("\n🚀 Ejecutando configuración completa del sistema...")
    
    try:
        # Ejecutar el script usando subprocess
        result = subprocess.run([
            sys.executable, 'setup_sistema_completo.py'
        ], cwd='/sisoc', check=True)
        
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
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'
        ], cwd='/sisoc', check=True)
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
    
    # Cambiar al directorio del proyecto
    os.chdir('/sisoc')
    
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