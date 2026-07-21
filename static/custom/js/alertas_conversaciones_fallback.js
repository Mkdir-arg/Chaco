/**
 * Fallback de notificaciones para Conversaciones (polling)
 * - No toca #alertas-counter
 * - Muestra popup persistente con X para cerrar
 * - Solo se activa si el WS de conversaciones no esta conectado
 */

(function () {
    const conversacionesAlertasConfig = window.conversacionesConfig || {};

    class AlertasConversacionesFallback {
        constructor() {
            this.polling = null;
            this.ultimoConteo = 0;
            this.popup = null;
            this.mensajesNuevos = 0;
        }

        tieneRolConversaciones() {
            const groups = window.userGroups || [];
            return groups.includes('Conversaciones') || groups.includes('OperadorCharla');
        }

        wsNoConectado() {
            try {
                const wsObj = window.alertasConversaciones;
                if (!wsObj || !wsObj.socket) return true;
                // 1 = OPEN
                return wsObj.socket.readyState !== 1;
            } catch (_) {
                return true;
            }
        }

        iniciar() {
            if (!this.tieneRolConversaciones()) return;

            // Darle tiempo al WS a conectar
            setTimeout(() => {
                if (this.wsNoConectado()) {
                    this.iniciarPolling();
                }
            }, 2000);

            // Monitorizar el estado del WS y detener fallback si conecta
            setInterval(() => {
                if (!this.wsNoConectado()) {
                    this.detenerPolling();
                }
            }, 3000);
        }

        iniciarPolling() {
            // baseline para no disparar popup con conteo ya existente
            this.verificar(true);
            this.polling = setInterval(() => this.verificar(false), 10000);
        }

        async verificar(onlyBaseline) {
            // Si el WS ya está conectado, detener y salir
            if (!this.wsNoConectado()) {
                this.detenerPolling();
                return;
            }
            const alertsCountUrl = conversacionesAlertasConfig.alertsCountUrl;
            if (!alertsCountUrl) {
                return;
            }
            try {
                const r = await fetch(alertsCountUrl);
                if (!r.ok) return;
                const data = await r.json();
                const count = data.count || 0;

                if (onlyBaseline) {
                    this.ultimoConteo = count;
                    return;
                }

                if (count > this.ultimoConteo) {
                    const delta = count - this.ultimoConteo;
                    this.mensajesNuevos += delta;
                    this.mostrarPopup();
                    this.reproducirSonido();
                }
                this.ultimoConteo = count;
            } catch (_) {
                // silencioso
            }
        }

        mostrarPopup() {
            if (this.popup) {
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
                        if (this.popup === popup) {
                            this.popup = null;
                            this.mensajesNuevos = 0;
                        }
                    }
                }
            );
            this.popup = popup || null;
        }

        actualizarPopup() {
            const contenido = this.popup?.querySelector('[data-toast-message]');
            if (contenido) {
                contenido.textContent = `Tenés ${this.mensajesNuevos} mensaje(s) nuevo(s).`;
            }
        }

        cerrarPopup() {
            if (this.popup) {
                window.ChacoToast?.dismiss(this.popup);
                this.popup = null;
                this.mensajesNuevos = 0;
            }
        }

        reproducirSonido() {
            try { if (window.notificationSound) window.notificationSound.playDoubleBeep(); } catch (_) {}
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        const fb = new AlertasConversacionesFallback();
        fb.iniciar();
        window.alertasConversacionesFallback = fb;
    });
})();
