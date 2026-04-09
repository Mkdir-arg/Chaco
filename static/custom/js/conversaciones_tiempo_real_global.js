// Sistema global de notificaciones para conversaciones
let ultimoConteoConversaciones = 0;
const conversacionesGlobalConfig = window.conversacionesConfig || {};

function verificarNuevasConversaciones() {
    const statsUrl = conversacionesGlobalConfig.statsUrl;
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
            const chatsNoAtendidos = data.estadisticas.chats_no_atendidos;
            
            // Si es la primera vez, solo guardar el valor
            if (ultimoConteoConversaciones === 0) {
                ultimoConteoConversaciones = chatsNoAtendidos;
                return;
            }
            
            // Si hay nuevas conversaciones
            if (chatsNoAtendidos > ultimoConteoConversaciones) {
                const nuevas = chatsNoAtendidos - ultimoConteoConversaciones;
                mostrarNotificacionGlobal(`🆕 ${nuevas} nueva(s) conversación(es) sin atender`, 'info');
                ultimoConteoConversaciones = chatsNoAtendidos;
            } else {
                ultimoConteoConversaciones = chatsNoAtendidos;
            }
        }
    })
    .catch(error => {
        console.error('Error verificando conversaciones:', error);
    });
}

function mostrarNotificacionGlobal(mensaje, tipo = 'info') {
    const listUrl = conversacionesGlobalConfig.listUrl || '#';
    // Remover notificaciones anteriores
    const notificacionesAnteriores = document.querySelectorAll('.notificacion-global-conversaciones');
    notificacionesAnteriores.forEach(n => n.remove());
    
    const notificacion = document.createElement('div');
    notificacion.className = `notificacion-global-conversaciones fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg text-white ${
        tipo === 'info' ? 'bg-blue-500' : 'bg-green-500'
    }`;
    notificacion.innerHTML = `
        <div class="flex items-center">
            <span>${mensaje}</span>
            <a href="${listUrl}" class="ml-3 bg-white text-blue-600 px-3 py-1 rounded text-sm hover:bg-gray-100">
                Ver
            </a>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-white hover:text-gray-200">
                ✕
            </button>
        </div>
    `;
    
    document.body.appendChild(notificacion);
    
    // Auto-remover después de 8 segundos
    setTimeout(() => {
        if (notificacion.parentElement) {
            notificacion.remove();
        }
    }, 8000);
}

// Inicializar solo si el usuario tiene permisos
document.addEventListener('DOMContentLoaded', function() {
    // Verificar cada 5 segundos
    setInterval(verificarNuevasConversaciones, 5000);
    
    // Primera verificación después de 2 segundos
    setTimeout(verificarNuevasConversaciones, 2000);
});
