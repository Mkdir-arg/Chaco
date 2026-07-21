class AlertasWebSocket {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 3000;
        this.init();
    }

    init() {
        this.connect();
        this.setupNotificationPermission();
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/alertas/`;
        
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
            console.log('Conectado a alertas WebSocket');
            this.reconnectAttempts = 0;
            this.showConnectionStatus(true);
        };
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.socket.onclose = () => {
            console.log('Desconectado de alertas WebSocket');
            this.showConnectionStatus(false);
            this.reconnect();
        };
        
        this.socket.onerror = (error) => {
            console.error('Error WebSocket:', error);
        };
    }

    handleMessage(data) {
        switch(data.type) {
            case 'nueva_alerta':
                this.showAlertaNotification(data.alerta);
                this.updateAlertasCounter();
                break;
            case 'alerta_critica':
                this.showAlertaCritica(data.alerta);
                this.updateAlertasCounter();
                break;
            case 'alerta_cerrada':
                this.removeAlertaFromUI(data.alerta_id);
                this.updateAlertasCounter();
                break;
        }
    }

    showAlertaNotification(alerta) {
        // Notificación toast
        this.showToast(alerta);
        
        // Notificación del navegador
        if (Notification.permission === 'granted') {
            new Notification(`Nueva Alerta - ${alerta.prioridad}`, {
                body: `${alerta.ciudadano}: ${alerta.mensaje}`,
                icon: '/static/custom/img/alert-icon.png',
                tag: `alerta-${alerta.id}`
            });
        }
        
        // Sonido para alertas críticas
        if (alerta.prioridad === 'CRITICA') {
            this.playAlertSound();
        }
    }

    showAlertaCritica(alerta) {
        this.showToast(alerta, { persistent: true, title: 'Alerta crítica' });
        this.playAlertSound();

        // Parpadeo en el título
        this.blinkTitle('🚨 ALERTA CRÍTICA');
    }

    showToast(alerta, options = {}) {
        const prioridad = String(alerta.prioridad || 'BAJA').toUpperCase();
        const type = prioridad === 'CRITICA' || prioridad === 'ALTA'
            ? 'error'
            : prioridad === 'MEDIA'
                ? 'warning'
                : 'info';
        const ciudadano = alerta.ciudadano || 'Sin ciudadano';
        const mensaje = alerta.mensaje || 'Se recibió una nueva alerta.';
        const legajoId = Number(alerta.legajo_id);

        window.ChacoToast?.show(`${ciudadano}: ${mensaje}`, {
            type,
            title: options.title || 'Nueva alerta',
            persistent: options.persistent ?? (type === 'warning' || type === 'error'),
            action: Number.isInteger(legajoId) && legajoId > 0
                ? { label: 'Ver legajo', href: `/legajos/${legajoId}/` }
                : undefined
        });
    }

    playAlertSound() {
        try {
            const audio = new Audio('/static/custom/sounds/alert.mp3');
            audio.volume = 0.5;
            audio.play().catch(() => {
                // Silenciar error si no se puede reproducir
            });
        } catch (e) {
            // Silenciar error
        }
    }

    blinkTitle(message) {
        const originalTitle = document.title;
        let isBlinking = true;
        
        const blink = setInterval(() => {
            document.title = isBlinking ? message : originalTitle;
            isBlinking = !isBlinking;
        }, 1000);
        
        // Detener después de 10 segundos
        setTimeout(() => {
            clearInterval(blink);
            document.title = originalTitle;
        }, 10000);
    }

    updateAlertasCounter() {
        // Actualizar contador de alertas en la UI
        const counter = document.querySelector('#alertas-counter');
        if (counter) {
            fetch('/legajos/alertas/count/')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    counter.textContent = data.count;
                    counter.classList.toggle('hidden', data.count === 0);
                    
                    // Cargar preview de alertas
                    this.loadAlertasPreview();
                })
                .catch(error => {
                    console.error('Error actualizando contador de alertas:', error);
                    counter.classList.add('hidden');
                });
        }
    }
    
    loadAlertasPreview() {
        const preview = document.querySelector('#alertas-preview');
        if (!preview) return;
        
        // Intentar primero el endpoint simple
        fetch('/legajos/alertas/preview/')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                const alertas = data.results || data;
                if (alertas && alertas.length > 0) {
                    preview.innerHTML = alertas.map(alerta => `
                        <div class="p-3 border-b border-gray-100 hover:bg-gray-50">
                            <div class="flex items-start justify-between">
                                <div class="flex-1">
                                    <p class="text-sm font-medium text-gray-900">${alerta.ciudadano_nombre || 'Sin ciudadano'}</p>
                                    <p class="text-xs text-gray-600 mt-1">${alerta.mensaje}</p>
                                    <p class="text-xs text-gray-400 mt-1">${new Date(alerta.creado).toLocaleString()}</p>
                                </div>
                                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                                    alerta.prioridad === 'CRITICA' ? 'bg-red-100 text-red-800' :
                                    alerta.prioridad === 'ALTA' ? 'bg-orange-100 text-orange-800' :
                                    alerta.prioridad === 'MEDIA' ? 'bg-yellow-100 text-yellow-800' :
                                    'bg-blue-100 text-blue-800'
                                }">
                                    ${alerta.prioridad}
                                </span>
                            </div>
                        </div>
                    `).join('');
                } else {
                    preview.innerHTML = `
                        <div class="p-4 text-center text-gray-500">
                            <i class="fas fa-check-circle text-green-500 text-2xl mb-2"></i>
                            <p>No hay alertas activas</p>
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Error cargando alertas:', error);
                // Fallback: intentar endpoint alternativo
                this.loadAlertasPreviewFallback();
            });
    }
    
    loadAlertasPreviewFallback() {
        const preview = document.querySelector('#alertas-preview');
        if (!preview) return;
        
        // Usar endpoint de views_alertas como fallback
        fetch('/legajos/alertas/count/')
            .then(response => response.json())
            .then(data => {
                if (data.count > 0) {
                    preview.innerHTML = `
                        <div class="p-4 text-center text-blue-600">
                            <i class="fas fa-bell text-2xl mb-2"></i>
                            <p class="font-medium">${data.count} alertas activas</p>
                            <p class="text-xs text-gray-500 mt-1">${data.criticas || 0} críticas</p>
                        </div>
                    `;
                } else {
                    preview.innerHTML = `
                        <div class="p-4 text-center text-gray-500">
                            <i class="fas fa-check-circle text-green-500 text-2xl mb-2"></i>
                            <p>No hay alertas activas</p>
                        </div>
                    `;
                }
            })
            .catch(() => {
                preview.innerHTML = `
                    <div class="p-4 text-center text-red-500">
                        <i class="fas fa-exclamation-triangle mb-2"></i>
                        <p>Error cargando alertas</p>
                    </div>
                `;
            });
    }

    removeAlertaFromUI(alertaId) {
        const alertElement = document.querySelector(`[data-alerta-id="${alertaId}"]`);
        if (alertElement) {
            alertElement.remove();
        }
    }

    setupNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    showConnectionStatus(connected) {
        const indicator = document.querySelector('#websocket-status');
        if (indicator) {
            indicator.className = connected ? 'text-green-500' : 'text-red-500';
            indicator.title = connected ? 'Conectado' : 'Desconectado';
        }
    }

    reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
                console.log(`Reintentando conexión... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                this.connect();
            }, this.reconnectInterval);
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.alertasWS = new AlertasWebSocket();
    
    // Cargar contador inicial
    setTimeout(() => {
        if (window.alertasWS) {
            window.alertasWS.updateAlertasCounter();
        }
    }, 1000);
});
