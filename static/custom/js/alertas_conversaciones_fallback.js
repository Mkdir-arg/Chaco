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

            const div = document.createElement('div');
            div.className = 'fixed top-4 right-4 bg-blue-600 text-white px-6 py-4 rounded-lg shadow-lg z-50 max-w-sm';
            div.innerHTML = `
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
            div.querySelector('button').addEventListener('click', () => this.cerrarPopup());
            document.body.appendChild(div);
            this.popup = div;
        }

        actualizarPopup() {
            if (!this.popup) return;
            const contenido = this.popup.querySelector('div div:last-child');
            if (contenido) {
                contenido.textContent = `Tienes ${this.mensajesNuevos} mensaje(s) nuevo(s)`;
            }
        }

        cerrarPopup() {
            if (this.popup) {
                this.popup.remove();
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
