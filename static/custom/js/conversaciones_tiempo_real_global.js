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
    window.ChacoToast?.show(mensaje, {
        type: tipo,
        duration: 8000,
        action: listUrl !== '#' ? { label: 'Ver', href: listUrl } : undefined
    });
}

// Inicializar solo si el usuario tiene permisos
document.addEventListener('DOMContentLoaded', function() {
    // Verificar cada 5 segundos
    setInterval(verificarNuevasConversaciones, 5000);
    
    // Primera verificación después de 2 segundos
    setTimeout(verificarNuevasConversaciones, 2000);
});
