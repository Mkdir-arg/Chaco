#!/bin/bash
echo "🚀 Iniciando sistema con optimizaciones..."

# Esperar a que MySQL esté listo
echo "⏳ Esperando MySQL..."
while ! python manage.py check --database default 2>/dev/null; do
    sleep 2
done

# Configurar sistema completo
echo "⚙️ Configurando sistema..."
python manage.py setup_system

echo "✅ Sistema iniciado y optimizado correctamente"

# Iniciar servidor
exec "$@"