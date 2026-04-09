/**
 * Generador de sonidos de notificación
 */

class NotificationSound {
    constructor() {
        this.audioContext = null;
        this.init();
    }

    init() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.warn('Audio context no disponible');
        }
    }

    playNotification() {
        if (!this.audioContext) return;

        try {
            // Crear oscilador para generar tono
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();

            // Conectar nodos
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);

            // Configurar sonido
            oscillator.frequency.setValueAtTime(800, this.audioContext.currentTime); // Frecuencia 800Hz
            oscillator.type = 'sine';

            // Configurar volumen con fade
            gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(0.1, this.audioContext.currentTime + 0.01);
            gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + 0.3);

            // Reproducir
            oscillator.start(this.audioContext.currentTime);
            oscillator.stop(this.audioContext.currentTime + 0.3);

        } catch (e) {
            console.warn('Error reproduciendo sonido:', e);
        }
    }

    playDoubleBeep() {
        this.playNotification();
        setTimeout(() => this.playNotification(), 200);
    }
}

// Instancia global
window.notificationSound = new NotificationSound();
