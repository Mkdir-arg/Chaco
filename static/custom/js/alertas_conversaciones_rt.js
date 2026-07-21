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

        let popup;
        popup = window.ChacoToast?.info(
            `Tenés ${this.mensajesNuevos} mensaje(s) nuevo(s).`,
            {
                title: 'Nuevos mensajes',
                persistent: true,
                onDismiss: () => {
                    if (this.popupActivo === popup) {
                        this.popupActivo = null;
                        this.mensajesNuevos = 0;
                    }
                }
            }
        );
        this.popupActivo = popup || null;
    }

    actualizarPopup() {
        const contenido = this.popupActivo?.querySelector('[data-toast-message]');
        if (contenido) {
            contenido.textContent = `Tenés ${this.mensajesNuevos} mensaje(s) nuevo(s).`;
        }
    }

    cerrarPopup() {
        if (this.popupActivo) {
            window.ChacoToast?.dismiss(this.popupActivo);
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
