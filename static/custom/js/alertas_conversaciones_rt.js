/**
 * Real-time chat alerts (WebSocket)
 * - Independent persistent popup
 * - Does not touch #alertas-counter
 * - Exposes window.alertasConversaciones with .socket so fallback can detect it
 */

class AlertasConversacionesRT {
    constructor() {
        this.socket = null;
        this.mensajesNuevos = 0;
        this.popupActivo = null;
        this.init();
    }

    init() {
        if (!this.tieneRolConversaciones()) return;
        this.conectarWebSocket();
        this.configurarEventos();
    }

    tieneRolConversaciones() {
        const userGroups = window.userGroups || [];
        return userGroups.includes('Conversaciones') || userGroups.includes('OperadorCharla') || (window.isSuperuser === true);
    }

    conectarWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/alertas-conversaciones/`;

            this.socket = new WebSocket(wsUrl);

            this.socket.onopen = () => {
                console.log('[Conversaciones] WS conectado');
            };

            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.manejarMensaje(data);
                } catch (_) {}
            };

            this.socket.onclose = () => {
                console.log('[Conversaciones] WS cerrado, reintentando en 3s...');
                setTimeout(() => this.conectarWebSocket(), 3000);
            };

            this.socket.onerror = () => {
                // silent
            };
        } catch (_) {
            // silent
        }
    }

    manejarMensaje(data) {
        if (data && data.type === 'nueva_alerta_conversacion') {
            this.mensajesNuevos += 1;
            this.mostrarPopup();
            this.reproducirSonido();
        }
    }

    mostrarPopup() {
        if (this.popupActivo) {
            this.actualizarPopup();
            return;
        }

        const cont = document.createElement('div');
        cont.className = 'fixed top-4 right-4 bg-blue-600 text-white px-6 py-4 rounded-lg shadow-lg z-50 max-w-sm';
        cont.innerHTML = `
            <div class="flex items-center justify-between">
                <div>
                    <div class="font-bold text-lg">Nuevos mensajes</div>
                    <div class="text-sm opacity-90">Tienes ${this.mensajesNuevos} mensaje(s) nuevo(s)</div>
                </div>
                <button class="ml-4 text-white hover:text-gray-200 text-xl font-bold" aria-label="Cerrar">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                    </svg>
                </button>
            </div>
        `;
        cont.querySelector('button').addEventListener('click', () => this.cerrarPopup());
        document.body.appendChild(cont);
        this.popupActivo = cont;
    }

    actualizarPopup() {
        if (!this.popupActivo) return;
        const contenido = this.popupActivo.querySelector('div div:last-child');
        if (contenido) contenido.textContent = `Tienes ${this.mensajesNuevos} mensaje(s) nuevo(s)`;
    }

    cerrarPopup() {
        if (this.popupActivo) {
            this.popupActivo.remove();
            this.popupActivo = null;
            this.mensajesNuevos = 0;
        }
    }

    reproducirSonido() {
        try { if (window.notificationSound) window.notificationSound.playDoubleBeep(); } catch (_) {}
    }

    configurarEventos() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.alertasConversaciones = new AlertasConversacionesRT();
});

