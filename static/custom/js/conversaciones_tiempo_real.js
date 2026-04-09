// Sistema de actualizaciones en tiempo real para conversaciones
let ultimosValores = {
    chats_no_atendidos: 0,
    atendidos_mes: 0,
    tiempo_promedio: 0
};
const conversacionesRealtimeConfig = window.conversacionesConfig || {};

function actualizarDatos() {
    const statsUrl = conversacionesRealtimeConfig.statsUrl;
    if (!statsUrl) return;

    fetch(statsUrl, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const stats = data.estadisticas;
            
            // Verificar si hay nuevas conversaciones
            const chatsElement = document.querySelector('[data-stat="chats-no-atendidos"]');
            if (chatsElement) {
                const valorActual = parseInt(chatsElement.textContent);
                const valorNuevo = stats.chats_no_atendidos;
                
                if (valorNuevo > valorActual) {
                    // Hay nuevas conversaciones - recargar página
                    mostrarNotificacion(`🆕 ${valorNuevo - valorActual} nueva(s) conversación(es)`, 'success');
                    // setTimeout(() => {
                    //     window.location.reload();
                    // }, 1000);
                    // return;
                }
                
                // Actualizar valor
                chatsElement.textContent = valorNuevo;
                
                // Resaltar si cambió
                if (valorActual !== valorNuevo) {
                    chatsElement.style.backgroundColor = '#fef3c7';
                    setTimeout(() => chatsElement.style.backgroundColor = '', 2000);
                }
            }
            
            // Actualizar otros valores
            const atendidosElement = document.querySelector('[data-stat="atendidos-mes"]');
            if (atendidosElement) {
                atendidosElement.textContent = stats.atendidos_mes;
            }
            
            const tiempoElement = document.querySelector('[data-stat="tiempo-promedio"]');
            if (tiempoElement) {
                tiempoElement.textContent = stats.tiempo_promedio + ' min';
            }
        }
    })
    .catch(error => {
        console.error('Error actualizando datos:', error);
    });
}

function mostrarNotificacion(mensaje, tipo = 'info') {
    // Remover notificaciones anteriores
    const notificacionesAnteriores = document.querySelectorAll('.notificacion-tiempo-real');
    notificacionesAnteriores.forEach(n => n.remove());
    
    const notificacion = document.createElement('div');
    notificacion.className = `notificacion-tiempo-real fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg text-white ${
        tipo === 'success' ? 'bg-green-500' : 'bg-blue-500'
    }`;
    notificacion.innerHTML = `
        <div class="flex items-center">
            <span>${mensaje}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                ✕
            </button>
        </div>
    `;
    
    document.body.appendChild(notificacion);
    
    // Auto-remover después de 4 segundos
    setTimeout(() => {
        if (notificacion.parentElement) {
            notificacion.remove();
        }
    }, 4000);
}

// Inicializar cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Sistema de tiempo real iniciado');
    
    // Actualizar cada 3 segundos
    setInterval(actualizarDatos, 3000);
    
    // Primera actualización después de 1 segundo
    setTimeout(actualizarDatos, 1000);
});
