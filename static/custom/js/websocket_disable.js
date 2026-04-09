// Deshabilitar WebSockets temporalmente para evitar 404s
// Los WebSockets requieren Daphne server, no Gunicorn+gevent

// Interceptar intentos de conexión WebSocket
if (typeof WebSocket !== 'undefined') {
    const originalWebSocket = WebSocket;
    window.WebSocket = function(url, protocols) {
        console.log('WebSocket deshabilitado temporalmente:', url);
        // Retornar objeto mock que no hace nada
        return {
            readyState: 3, // CLOSED
            close: function() {},
            send: function() {},
            addEventListener: function() {},
            removeEventListener: function() {}
        };
    };
}
