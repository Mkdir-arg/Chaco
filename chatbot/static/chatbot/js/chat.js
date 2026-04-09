class ChatInterface {
    constructor() {
        this.currentConversationId = null;
        this.isLoading = false;
        this.appElement = document.getElementById('chatbot-app');
        this.initializeElements();
        this.bindEvents();
        this.loadActiveConversation();
    }

    get urls() {
        return {
            sendMessage: this.appElement.dataset.sendUrl,
            submitFeedback: this.appElement.dataset.feedbackUrl,
            newConversation: this.appElement.dataset.newUrl,
            conversationTemplate: this.appElement.dataset.conversationUrlTemplate,
        };
    }

    initializeElements() {
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.messagesContainer = document.getElementById('messages-container');
        this.conversationsList = document.getElementById('conversations-list');
        this.newConversationBtn = document.getElementById('new-conversation');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.welcomeMessage = document.getElementById('welcome-message');
    }

    bindEvents() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.newConversationBtn.addEventListener('click', () => this.createNewConversation());

        // Event delegation para conversaciones
        this.conversationsList.addEventListener('click', (e) => {
            const conversationItem = e.target.closest('.conversation-item');
            if (conversationItem) {
                const conversationId = conversationItem.dataset.conversationId;
                this.loadConversation(conversationId);
            }
        });
    }

    loadActiveConversation() {
        const activeConversation = document.querySelector('.conversation-item');
        if (activeConversation) {
            const conversationId = activeConversation.dataset.conversationId;
            this.loadConversation(conversationId);
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isLoading) return;

        this.isLoading = true;
        this.updateUI(true);
        
        // Limpiar input
        this.messageInput.value = '';
        
        // Ocultar mensaje de bienvenida
        if (this.welcomeMessage) {
            this.welcomeMessage.style.display = 'none';
        }

        try {
            const response = await fetch(this.urls.sendMessage, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: this.currentConversationId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.currentConversationId = data.conversation_id;
                this.displayMessage(data.user_message, 'user');
                this.displayMessage(data.assistant_message, 'assistant');
                this.updateConversationsList();
            } else {
                this.showError(data.error || 'Error al enviar mensaje');
            }
        } catch (error) {
            this.showError('Error de conexión');
            console.error('Error:', error);
        } finally {
            this.isLoading = false;
            this.updateUI(false);
        }
    }

    displayMessage(messageData, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const timestamp = new Date(messageData.timestamp).toLocaleTimeString('es-AR', {
            hour: '2-digit',
            minute: '2-digit'
        });

        messageDiv.innerHTML = `
            <div class="message-bubble">
                ${this.formatMessageContent(messageData.content)}
            </div>
            <div class="message-time">${timestamp}</div>
            ${role === 'assistant' ? this.getFeedbackButtons(messageData.id) : ''}
        `;

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatMessageContent(content) {
        // Convertir saltos de línea a <br>
        return content.replace(/\n/g, '<br>');
    }

    getFeedbackButtons(messageId) {
        return `
            <div class="feedback-buttons mt-2 flex space-x-2">
                <button onclick="chatInterface.submitFeedback(${messageId}, 5)" 
                        class="text-green-600 hover:text-green-800 text-sm">
                    👍 Útil
                </button>
                <button onclick="chatInterface.submitFeedback(${messageId}, 1)" 
                        class="text-red-600 hover:text-red-800 text-sm">
                    👎 No útil
                </button>
            </div>
        `;
    }

    async submitFeedback(messageId, rating) {
        try {
            await fetch(this.urls.submitFeedback, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    message_id: messageId,
                    rating: rating
                })
            });
            
            // Mostrar confirmación visual
            this.showNotification('¡Gracias por tu feedback!');
        } catch (error) {
            console.error('Error al enviar feedback:', error);
        }
    }

    async loadConversation(conversationId) {
        try {
            const response = await fetch(this.urls.conversationTemplate.replace('__ID__', conversationId));
            const data = await response.json();

            this.currentConversationId = conversationId;
            this.clearMessages();
            
            if (this.welcomeMessage) {
                this.welcomeMessage.style.display = 'none';
            }

            data.messages.forEach(message => {
                this.displayMessage(message, message.role);
            });

            this.setActiveConversation(conversationId);
        } catch (error) {
            this.showError('Error al cargar conversación');
            console.error('Error:', error);
        }
    }

    async createNewConversation() {
        try {
            const response = await fetch(this.urls.newConversation, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();
            this.currentConversationId = data.conversation_id;
            this.clearMessages();
            
            if (this.welcomeMessage) {
                this.welcomeMessage.style.display = 'block';
            }

            this.updateConversationsList();
        } catch (error) {
            this.showError('Error al crear conversación');
            console.error('Error:', error);
        }
    }

    clearMessages() {
        const messages = this.messagesContainer.querySelectorAll('.message');
        messages.forEach(message => message.remove());
    }

    setActiveConversation(conversationId) {
        // Remover clase active de todas las conversaciones
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });

        // Agregar clase active a la conversación actual
        const activeItem = document.querySelector(`[data-conversation-id="${conversationId}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }

    updateConversationsList() {
        // Recargar la página para actualizar la lista de conversaciones
        // En una implementación más avanzada, esto se haría con AJAX
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    }

    updateUI(loading) {
        this.sendButton.disabled = loading;
        this.messageInput.disabled = loading;
        
        if (loading) {
            this.sendButton.textContent = 'Enviando...';
            this.typingIndicator.classList.remove('hidden');
        } else {
            this.sendButton.textContent = 'Enviar';
            this.typingIndicator.classList.add('hidden');
        }
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message assistant';
        errorDiv.innerHTML = `
            <div class="message-bubble bg-red-100 text-red-800 border border-red-200">
                ❌ ${message}
            </div>
        `;
        this.messagesContainer.appendChild(errorDiv);
        this.scrollToBottom();
    }

    showNotification(message) {
        // Crear notificación temporal
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.chatInterface = new ChatInterface();
});
