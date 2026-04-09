/**
 * Sistema de alertas para conversaciones
 * Maneja notificaciones en tiempo real para operadores con rol Conversaciones
 */

class AlertasConversaciones {
    constructor() {
        this.socket = null;
        this.mensajesNuevos = 0;
        this.popupActivo = null;
        this.init();
    }

    init() {
        if (!this.tieneRolConversaciones()) {
            return;
        }
        this.conectarWebSocket();
        this.configurarEventos();
    }

    tieneRolConversaciones() {
        const userGroups = window.userGroups || [];
        return userGroups.includes('Conversaciones') || userGroups.includes('OperadorCharla');
    }

    conectarWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/alertas-conversaciones/`;
        
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
            console.log('Conectado a alertas de conversaciones');
        };
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.manejarMensaje(data);
        };
        
        this.socket.onclose = () => {
            setTimeout(() => this.conectarWebSocket(), 3000);
        };
    }

    manejarMensaje(data) {
        if (data.type === 'nueva_alerta_conversacion') {
            this.mensajesNuevos++;
            this.mostrarPopup();
            this.reproducirSonido();
        }
    }

    mostrarPopup() {
        if (this.popupActivo) {
            this.actualizarPopup();
            return;
        }

        this.popupActivo = document.createElement('div');
        this.popupActivo.className = 'fixed top-4 right-4 bg-blue-600 text-white px-6 py-4 rounded-lg shadow-lg z-50 max-w-sm';
        this.popupActivo.innerHTML = `
            <div class="flex items-center justify-between">
                <div>
                    <div class="font-bold text-lg">Nuevos mensajes</div>
                    <div class="text-sm opacity-90">Tienes ${this.mensajesNuevos} mensaje(s) nuevo(s)</div>
                </div>
                <button onclick="window.alertasConversaciones.cerrarPopup()" class="ml-4 text-white hover:text-gray-200 text-xl font-bold">
                    ×
                </button>
            </div>
        `;
        
        document.body.appendChild(this.popupActivo);
    }

    actualizarPopup() {
        if (this.popupActivo) {
            const contenido = this.popupActivo.querySelector('div div:last-child');
            if (contenido) {
                contenido.textContent = `Tienes ${this.mensajesNuevos} mensaje(s) nuevo(s)`;
            }
        }
    }

    cerrarPopup() {
        if (this.popupActivo) {
            this.popupActivo.remove();
            this.popupActivo = null;
            this.mensajesNuevos = 0;
        }
    }



    reproducirSonido() {
        try {
            if (window.notificationSound) {
                window.notificationSound.playDoubleBeep();
            }
        } catch (e) {}
    }

    configurarEventos() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.alertasConversaciones = new AlertasConversaciones();
});
