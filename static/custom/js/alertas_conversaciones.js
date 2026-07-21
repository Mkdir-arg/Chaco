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
