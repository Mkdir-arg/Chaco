/*
 * API global de notificaciones transitorias.
 * Los mensajes se crean con nodos de texto para no interpolar HTML no confiable.
 */
(function () {
    'use strict';

    const MAX_VISIBLE = 3;
    const AUTO_DISMISS_MS = 5000;
    const LEAVE_ANIMATION_MS = 180;
    const LEVEL_TYPES = {
        10: 'info',
        20: 'info',
        25: 'success',
        30: 'warning',
        40: 'error'
    };
    const TYPE_DETAILS = {
        success: { icon: 'fa-check-circle', title: 'Operación exitosa' },
        info: { icon: 'fa-info-circle', title: 'Información' },
        warning: { icon: 'fa-exclamation-triangle', title: 'Advertencia' },
        error: { icon: 'fa-exclamation-circle', title: 'Error' }
    };

    let viewport;
    let initialized = false;
    const queue = [];
    const active = new Set();

    function normaliseType(value) {
        const candidate = String(value || 'info').trim().toLowerCase();
        const aliases = {
            success: 'success',
            exito: 'success',
            'éxito': 'success',
            ok: 'success',
            info: 'info',
            information: 'info',
            debug: 'info',
            warning: 'warning',
            advertencia: 'warning',
            warn: 'warning',
            error: 'error',
            danger: 'error',
            critica: 'error',
            'crítica': 'error',
            critical: 'error',
            alta: 'error'
        };

        return aliases[candidate] || 'info';
    }

    function messageText(value) {
        if (typeof value === 'string') {
            return value;
        }

        if (value && typeof value === 'object') {
            return value.responseJSON?.error
                || value.responseJSON?.message
                || value.statusText
                || value.message
                || 'Ocurrió un error al completar la operación.';
        }

        return String(value || '');
    }

    function getViewport() {
        if (viewport && document.body.contains(viewport)) {
            return viewport;
        }

        viewport = document.getElementById('toast-viewport');
        if (!viewport && document.body) {
            viewport = document.createElement('div');
            viewport.id = 'toast-viewport';
            viewport.className = 'toast-viewport';
            viewport.setAttribute('aria-live', 'polite');
            viewport.setAttribute('aria-relevant', 'additions text');
            document.body.appendChild(viewport);
        }

        return viewport;
    }

    function typeFromToast(toast) {
        const level = Number(toast.dataset.toastLevel);
        return normaliseType(toast.dataset.toastType || LEVEL_TYPES[level]);
    }

    function isPersistent(toast, type) {
        if (toast.dataset.toastPersistent === 'true') {
            return true;
        }

        if (toast.dataset.toastPersistent === 'false') {
            return false;
        }

        return type === 'warning' || type === 'error';
    }

    function applyType(toast, type) {
        const details = TYPE_DETAILS[type];
        toast.classList.remove('toast--success', 'toast--info', 'toast--warning', 'toast--error');
        toast.classList.add(`toast--${type}`);
        toast.dataset.toastType = type;
        toast.setAttribute('role', type === 'error' ? 'alert' : 'status');
        toast.setAttribute('aria-live', type === 'error' ? 'assertive' : 'polite');

        const icon = toast.querySelector('[data-toast-icon]');
        if (icon) {
            icon.className = `fas ${details.icon}`;
            icon.setAttribute('aria-hidden', 'true');
        }

        const title = toast.querySelector('[data-toast-title]');
        if (title && !title.textContent.trim()) {
            title.textContent = details.title;
        }
    }

    function createToast(message, options) {
        const toast = document.createElement('section');
        toast.className = 'toast';
        toast.dataset.toast = 'true';
        if (typeof options.persistent === 'boolean') {
            toast.dataset.toastPersistent = String(options.persistent);
        }
        if (Number.isFinite(Number(options.duration))) {
            toast.dataset.toastDuration = String(options.duration);
        }

        const icon = document.createElement('span');
        icon.className = 'toast__icon';
        icon.dataset.toastIcon = 'true';

        const content = document.createElement('div');
        content.className = 'toast__content';

        const title = document.createElement('p');
        title.className = 'toast__title';
        title.dataset.toastTitle = 'true';
        title.textContent = options.title || '';

        const body = document.createElement('p');
        body.className = 'toast__message';
        body.dataset.toastMessage = 'true';
        body.textContent = messageText(message);

        if (title.textContent) {
            content.appendChild(title);
        }
        content.appendChild(body);

        if (options.action && options.action.label) {
            const action = document.createElement(options.action.href ? 'a' : 'button');
            action.className = 'toast__action';
            action.textContent = options.action.label;
            if (options.action.href) {
                action.href = options.action.href;
            } else {
                action.type = 'button';
                action.addEventListener('click', function () {
                    options.action.onClick?.(toast);
                });
            }
            content.appendChild(action);
        }

        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'toast__close';
        closeButton.dataset.toastDismiss = 'true';
        closeButton.setAttribute('aria-label', 'Cerrar notificación');
        closeButton.innerHTML = '<i class="fas fa-times" aria-hidden="true"></i>';

        toast.append(icon, content, closeButton);
        toast.__toastBeforeDismiss = options.beforeDismiss;
        toast.__toastOnDismiss = options.onDismiss;
        applyType(toast, normaliseType(options.type));

        return toast;
    }

    function getCsrfToken() {
        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        if (input && input.value) {
            return input.value;
        }

        const meta = document.querySelector('meta[name=csrf-token]');
        if (meta && meta.content) {
            return meta.content;
        }

        const csrfCookie = document.cookie
            .split('; ')
            .find(function (cookie) { return cookie.startsWith('csrftoken='); });
        return csrfCookie ? decodeURIComponent(csrfCookie.split('=').slice(1).join('=')) : null;
    }

    function configureServerDismiss(toast) {
        const closeUrl = toast.dataset.toastCloseUrl;
        if (!closeUrl || toast.__toastBeforeDismiss) {
            return;
        }

        toast.__toastBeforeDismiss = async function () {
            const csrfToken = getCsrfToken();
            if (!csrfToken) {
                api.error('No se pudo cerrar la alerta crítica.');
                return false;
            }

            try {
                const response = await fetch(closeUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken
                    },
                    body: ''
                });
                const data = await response.json();

                if (!response.ok || !data.success) {
                    api.error(data.error || 'No se pudo cerrar la alerta crítica.');
                    return false;
                }

                return true;
            } catch (error) {
                console.error('No se pudo cerrar la alerta crítica.', error);
                api.error('No se pudo cerrar la alerta crítica.');
                return false;
            }
        };
    }

    function wireToast(toast) {
        if (toast.dataset.toastWired === 'true') {
            return toast;
        }

        const type = typeFromToast(toast);
        applyType(toast, type);
        configureServerDismiss(toast);
        toast.dataset.toastWired = 'true';

        const closeButton = toast.querySelector('[data-toast-dismiss]');
        if (closeButton) {
            closeButton.addEventListener('click', function () {
                dismiss(toast, 'manual');
            });
        }

        return toast;
    }

    function scheduleDismiss(toast) {
        const type = typeFromToast(toast);
        if (isPersistent(toast, type)) {
            return;
        }

        const duration = Number(toast.dataset.toastDuration) || AUTO_DISMISS_MS;
        toast.__toastTimer = window.setTimeout(function () {
            dismiss(toast, 'timeout');
        }, duration);
    }

    function activate(toast) {
        const root = getViewport();
        if (!root) {
            return;
        }

        wireToast(toast);
        root.appendChild(toast);
        active.add(toast);
        scheduleDismiss(toast);
    }

    function drainQueue() {
        while (active.size < MAX_VISIBLE && queue.length) {
            activate(queue.shift());
        }
    }

    function notifyDismiss(toast, reason) {
        const callback = toast.__toastOnDismiss;
        toast.__toastOnDismiss = null;

        if (typeof callback !== 'function') {
            return;
        }

        try {
            callback({ toast: toast, reason: reason });
        } catch (error) {
            console.error('No se pudo ejecutar el cierre de la notificación.', error);
        }
    }

    async function dismiss(toast, reason) {
        if (!toast || !active.has(toast) || toast.dataset.toastDismissing === 'true') {
            return false;
        }

        if (reason === 'manual' && typeof toast.__toastBeforeDismiss === 'function') {
            toast.classList.add('toast--pending');
            try {
                const mayDismiss = await toast.__toastBeforeDismiss();
                if (mayDismiss === false) {
                    toast.classList.remove('toast--pending');
                    return false;
                }
            } catch (error) {
                console.error('No se pudo cerrar la notificación.', error);
                toast.classList.remove('toast--pending');
                return false;
            }
            toast.classList.remove('toast--pending');
        }

        toast.dataset.toastDismissing = 'true';
        window.clearTimeout(toast.__toastTimer);
        notifyDismiss(toast, reason);
        toast.classList.add('toast--leaving');

        window.setTimeout(function () {
            toast.remove();
            active.delete(toast);
            drainQueue();
        }, LEAVE_ANIMATION_MS);

        return true;
    }

    function show(message, options) {
        const normalizedOptions = typeof message === 'object' && message !== null
            ? message
            : options || {};
        const normalizedMessage = typeof message === 'object' && message !== null
            ? message.message
            : message;
        const toast = createToast(normalizedMessage, normalizedOptions);
        queue.push(toast);

        if (initialized) {
            drainQueue();
        }

        return toast;
    }

    function legacyOptions(options) {
        const source = options && typeof options === 'object' ? options : {};
        const timeout = Number(source.timeOut);
        return {
            duration: Number.isFinite(timeout) && timeout > 0 ? timeout : undefined,
            persistent: source.timeOut === 0 ? true : undefined
        };
    }

    function createLegacyToastrAdapter() {
        const adapter = { options: {} };
        ['success', 'info', 'warning', 'error'].forEach(function (type) {
            const notify = function (message, _title, options) {
                return api.show(messageText(message), Object.assign({}, legacyOptions(adapter.options), legacyOptions(options), { type: type }));
            };
            adapter[type] = notify;
            adapter[type.charAt(0).toUpperCase() + type.slice(1)] = notify;
        });
        return adapter;
    }

    function initialise() {
        if (initialized) {
            return;
        }

        const root = getViewport();
        if (!root) {
            return;
        }

        Array.from(root.querySelectorAll('[data-toast]')).forEach(function (toast) {
            root.removeChild(toast);
            queue.push(toast);
        });

        initialized = true;
        drainQueue();
    }

    const api = {
        show: show,
        success: function (message, options) {
            return show(message, Object.assign({}, options, { type: 'success' }));
        },
        info: function (message, options) {
            return show(message, Object.assign({}, options, { type: 'info' }));
        },
        warning: function (message, options) {
            return show(message, Object.assign({}, options, { type: 'warning' }));
        },
        error: function (message, options) {
            return show(message, Object.assign({}, options, { type: 'error' }));
        },
        dismiss: function (toast) {
            return dismiss(toast, 'manual');
        }
    };

    window.ChacoToast = api;
    window.toastr = createLegacyToastrAdapter();
    window.showSuccessAlert = api.success;
    window.showErrorAlert = api.error;
    window.showWarningAlert = api.warning;

    const nativeAlert = window.alert.bind(window);
    window.alert = function (message) {
        try {
            api.info(messageText(message));
        } catch (error) {
            nativeAlert(message);
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialise);
    } else {
        initialise();
    }
})();
