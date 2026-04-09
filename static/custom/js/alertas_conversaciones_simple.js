/**
 * Sistema de alertas para conversaciones (versión simple sin WebSocket)
 */
const conversacionesSimpleConfig = window.conversacionesConfig || {};

class AlertasConversacionesSimple {
    constructor() {
        this.pollingInterval = null;
        this.ultimoConteo = 0;
        this.init();
    }

    init() {
        // Solo inicializar si el usuario tiene rol de conversaciones
        if (!this.tieneRolConversaciones()) {
            return;
        }

        this.iniciarPolling();
        this.configurarEventos();
    }

    tieneRolConversaciones() {
        const userGroups = window.userGroups || [];
        return userGroups.includes('Conversaciones') || userGroups.includes('OperadorCharla');
    }

    iniciarPolling() {
        // Verificar inmediatamente
        this.verificarAlertas();
        
        // Polling cada 10 segundos
        this.pollingInterval = setInterval(() => {
            this.verificarAlertas();
        }, 10000);
    }

    async verificarAlertas() {
        const alertsCountUrl = conversacionesSimpleConfig.alertsCountUrl;
        if (!alertsCountUrl) return;

        try {
            const response = await fetch(alertsCountUrl);
            if (!response.ok) return;
            
            const data = await response.json();
            const nuevoConteo = data.count || 0;
            
            // Solo mostrar notificación si es la primera vez que hay alertas
            if (nuevoConteo > 0 && this.ultimoConteo === 0) {
                this.mostrarNuevaAlerta(nuevoConteo);
                this.reproducirSonido();
            }
            
            this.ultimoConteo = nuevoConteo;
            this.actualizarContadorUI(nuevoConteo);
            
            // Solo actualizar preview si hay alertas
            if (nuevoConteo > 0) {
                this.actualizarPreview();
            }
            
        } catch (error) {
            console.error('Error verificando alertas:', error);
        }
    }

    actualizarContadorUI(count) {
        const contador = document.getElementById('alertas-counter');
        if (!contador) return;
        
        // Obtener contador actual del sistema principal
        const contadorActual = parseInt(contador.textContent) || 0;
        
        // Si hay alertas de conversaciones, sumarlas
        if (count > 0) {
            const nuevoTotal = contadorActual + count;
            contador.textContent = nuevoTotal;
            contador.classList.remove('hidden');
            contador.classList.add('animate-pulse');
        } else if (contadorActual === 0) {
            contador.classList.add('hidden');
            contador.classList.remove('animate-pulse');
        }
    }

    async actualizarPreview() {
        const preview = document.getElementById('alertas-preview');
        if (!preview) return;
        const alertsPreviewUrl = conversacionesSimpleConfig.alertsPreviewUrl;
        const detailTemplate = conversacionesSimpleConfig.detailUrlTemplate;
        if (!alertsPreviewUrl || !detailTemplate) return;
        
        try {
            const response = await fetch(alertsPreviewUrl);
            if (!response.ok) return;
            
            const data = await response.json();
            const alertas = data.results || [];
            
            if (alertas.length > 0) {
                // Agregar alertas de conversaciones al preview existente
                const alertasHTML = alertas.map(alerta => {
                    const esRiesgo = alerta.contenido && this.contieneRiesgo(alerta.contenido);
                    const claseRiesgo = esRiesgo ? 'bg-red-50 border-red-200' : 'hover:bg-gray-50';
                    const iconoRiesgo = esRiesgo ? 'fas fa-exclamation-triangle text-red-600' : 'fas fa-comment-dots text-blue-500';
                    const badgeRiesgo = esRiesgo ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800';
                    const textoRiesgo = esRiesgo ? 'RIESGO' : 'MENSAJE';
                    
                    return `
                        <div class="p-3 border-b border-gray-100 ${claseRiesgo} cursor-pointer" 
                             onclick="window.location.href='${detailTemplate.replace('/0/', `/${alerta.conversacion_id}/`)}'">
                            <div class="flex items-start justify-between">
                                <div class="flex-1">
                                    <p class="text-sm font-medium text-gray-900">
                                        <i class="${iconoRiesgo} mr-1"></i>
                                        ${alerta.ciudadano_nombre}
                                    </p>
                                    <p class="text-xs text-gray-600 mt-1">${alerta.contenido}</p>
                                    <p class="text-xs text-gray-400 mt-1">${alerta.fecha}</p>
                                </div>
                                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${badgeRiesgo}">
                                    ${textoRiesgo}
                                </span>
                            </div>
                        </div>
                    `;
                }).join('');
                
                // Reemplazar todo el contenido para evitar duplicados
                preview.innerHTML = alertasHTML;
            }
        } catch (error) {
            console.error('Error actualizando preview:', error);
        }
    }
    
    contieneRiesgo(contenido) {
        const palabrasRiesgo = ['suicidio', 'lastimar', 'drogas', 'violencia', 'matar', 'morir', 'suicidar'];
        const contenidoLower = contenido.toLowerCase();
        return palabrasRiesgo.some(palabra => contenidoLower.includes(palabra));
    }

    mostrarNuevaAlerta(cantidad) {
        // Toast notification
        this.mostrarToast(cantidad);
        
        // Notificación del navegador
        if (Notification.permission === 'granted') {
            new Notification('Nuevos mensajes en conversaciones', {
                body: `Tienes ${cantidad} mensaje(s) nuevo(s)`,
                icon: '/static/custom/img/logo.png'
            });
        }
    }

    mostrarToast(cantidad) {
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 bg-blue-600 text-white px-4 py-3 rounded-lg shadow-lg z-50 max-w-sm animate-slide-in';
        toast.innerHTML = `
            <div class="flex items-start">
                <i class="fas fa-comment-dots mr-2 mt-1"></i>
                <div class="flex-1">
                    <div class="font-medium">Nuevos mensajes</div>
                    <div class="text-sm opacity-90">Tienes ${cantidad} mensaje(s) nuevo(s)</div>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-white hover:text-gray-200">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }
    
    mostrarToastRiesgo(mensaje) {
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 bg-red-600 text-white px-4 py-3 rounded-lg shadow-lg z-50 max-w-sm animate-slide-in animate-pulse';
        toast.innerHTML = `
            <div class="flex items-start">
                <i class="fas fa-exclamation-triangle mr-2 mt-1"></i>
                <div class="flex-1">
                    <div class="font-bold">¡ALERTA DE RIESGO!</div>
                    <div class="text-sm opacity-90">Palabras de riesgo detectadas</div>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-white hover:text-gray-200">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remover después de 10 segundos (más tiempo para riesgo)
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 10000);
    }

    reproducirSonido() {
        try {
            if (window.notificationSound) {
                window.notificationSound.playDoubleBeep();
            }
        } catch (e) {
            console.warn('No se pudo reproducir sonido:', e);
        }
    }

    configurarEventos() {
        // Solicitar permisos de notificación
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
        
        // Limpiar contador cuando se hace clic en el dropdown
        const alertasDropdown = document.querySelector('[x-data*="showDropdown"]');
        if (alertasDropdown) {
            alertasDropdown.addEventListener('click', () => {
                setTimeout(() => {
                    this.marcarComoVisto();
                }, 1000);
            });
        }
    }

    async marcarComoVisto() {
        // Resetear contador local para permitir nueva notificación
        this.ultimoConteo = 0;
    }

    destruir() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
    }
}

// CSS para animaciones
const style = document.createElement('style');
style.textContent = `
    @keyframes slide-in {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    .animate-slide-in {
        animation: slide-in 0.3s ease-out;
    }
`;
document.head.appendChild(style);

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.alertasConversaciones = new AlertasConversacionesSimple();
});

// Limpiar al salir de la página
window.addEventListener('beforeunload', () => {
    if (window.alertasConversaciones) {
        window.alertasConversaciones.destruir();
    }
});
