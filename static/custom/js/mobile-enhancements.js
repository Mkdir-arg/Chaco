/**
 * Mobile Enhancements for NODO
 * Mejoras específicas para dispositivos móviles
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Detectar si es dispositivo móvil
    const isMobile = window.innerWidth <= 768;
    const isTablet = window.innerWidth > 768 && window.innerWidth <= 1024;
    
    // Agregar clases CSS según el dispositivo
    if (isMobile) {
        document.body.classList.add('is-mobile');
    } else if (isTablet) {
        document.body.classList.add('is-tablet');
    } else {
        document.body.classList.add('is-desktop');
    }
    
    // Mejorar el comportamiento de los dropdowns en móvil
    enhanceDropdowns();
    
    // Mejorar las tablas en móvil
    enhanceTables();
    
    // Mejorar los formularios en móvil
    enhanceForms();
    
    // Agregar soporte para swipe gestures
    addSwipeSupport();
    
    // Mejorar la navegación táctil
    enhanceTouchNavigation();
    
    // Auto-hide de elementos en scroll (móvil)
    if (isMobile) {
        addScrollBehavior();
    }
    
    // Lazy loading para imágenes
    addLazyLoading();
    
    // Mejorar modales en móvil
    enhanceModals();
});

/**
 * Mejorar dropdowns para dispositivos táctiles
 */
function enhanceDropdowns() {
    const dropdowns = document.querySelectorAll('select');
    
    dropdowns.forEach(dropdown => {
        // Agregar clase para mejor styling en móvil
        dropdown.classList.add('touch-friendly');
        
        // Mejorar el comportamiento en iOS
        if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
            dropdown.style.fontSize = '16px'; // Prevenir zoom en iOS
        }
    });
}

/**
 * Mejorar tablas para móvil
 */
function enhanceTables() {
    const tables = document.querySelectorAll('table');
    
    tables.forEach(table => {
        // Agregar scroll horizontal suave
        const wrapper = table.closest('.overflow-x-auto');
        if (wrapper) {
            wrapper.style.scrollBehavior = 'smooth';
            wrapper.style.webkitOverflowScrolling = 'touch';
        }
        
        // Agregar indicador de scroll horizontal
        if (table.scrollWidth > table.clientWidth) {
            addScrollIndicator(table);
        }
    });
}

/**
 * Agregar indicador de scroll horizontal
 */
function addScrollIndicator(table) {
    const wrapper = table.closest('.overflow-x-auto');
    if (!wrapper) return;
    
    const indicator = document.createElement('div');
    indicator.className = 'scroll-indicator';
    indicator.innerHTML = '<i class="fas fa-arrow-right"></i> Desliza para ver más';
    indicator.style.cssText = `
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        background: rgba(0,0,0,0.7);
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        pointer-events: none;
        z-index: 10;
    `;
    
    wrapper.style.position = 'relative';
    wrapper.appendChild(indicator);
    
    // Ocultar indicador después de scroll
    wrapper.addEventListener('scroll', function() {
        if (this.scrollLeft > 50) {
            indicator.style.opacity = '0';
        }
    });
}

/**
 * Mejorar formularios para móvil
 */
function enhanceForms() {
    const inputs = document.querySelectorAll('input, textarea');
    
    inputs.forEach(input => {
        // Prevenir zoom en iOS
        if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
            if (input.type !== 'file') {
                input.style.fontSize = '16px';
            }
        }
        
        // Mejorar inputs de fecha en móvil
        if (input.type === 'date' && window.innerWidth <= 768) {
            input.setAttribute('pattern', '[0-9]{2}/[0-9]{2}/[0-9]{4}');
        }
        
        // Auto-scroll al input activo en móvil
        if (window.innerWidth <= 768) {
            input.addEventListener('focus', function() {
                setTimeout(() => {
                    this.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'center' 
                    });
                }, 300);
            });
        }
    });
}

/**
 * Agregar soporte para gestos de swipe
 */
function addSwipeSupport() {
    let startX, startY, distX, distY;
    const threshold = 100; // Distancia mínima para considerar swipe
    
    document.addEventListener('touchstart', function(e) {
        const touch = e.touches[0];
        startX = touch.clientX;
        startY = touch.clientY;
    });
    
    document.addEventListener('touchend', function(e) {
        if (!startX || !startY) return;
        
        const touch = e.changedTouches[0];
        distX = touch.clientX - startX;
        distY = touch.clientY - startY;
        
        // Swipe horizontal
        if (Math.abs(distX) > Math.abs(distY) && Math.abs(distX) > threshold) {
            if (distX > 0) {
                // Swipe right - abrir sidebar si está cerrado
                const sidebarToggle = document.querySelector('[x-data]');
                if (sidebarToggle && window.innerWidth <= 1024) {
                    // Trigger Alpine.js sidebar open
                    sidebarToggle._x_dataStack[0].sidebarOpen = true;
                }
            } else {
                // Swipe left - cerrar sidebar si está abierto
                const sidebarToggle = document.querySelector('[x-data]');
                if (sidebarToggle && window.innerWidth <= 1024) {
                    // Trigger Alpine.js sidebar close
                    sidebarToggle._x_dataStack[0].sidebarOpen = false;
                }
            }
        }
        
        startX = startY = null;
    });
}

/**
 * Mejorar navegación táctil
 */
function enhanceTouchNavigation() {
    const touchTargets = document.querySelectorAll('button, a, [role="button"]');
    
    touchTargets.forEach(target => {
        // Asegurar que los elementos táctiles tengan el tamaño mínimo
        const rect = target.getBoundingClientRect();
        if (rect.width < 44 || rect.height < 44) {
            target.style.minWidth = '44px';
            target.style.minHeight = '44px';
            target.style.display = 'inline-flex';
            target.style.alignItems = 'center';
            target.style.justifyContent = 'center';
        }
        
        // Agregar feedback táctil
        target.addEventListener('touchstart', function() {
            this.style.opacity = '0.7';
        });
        
        target.addEventListener('touchend', function() {
            this.style.opacity = '';
        });
        
        target.addEventListener('touchcancel', function() {
            this.style.opacity = '';
        });
    });
}

/**
 * Comportamiento de scroll para móvil
 */
function addScrollBehavior() {
    let lastScrollTop = 0;
    const navbar = document.querySelector('.sticky');
    
    if (!navbar) return;
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // Scrolling down - hide navbar
            navbar.style.transform = 'translateY(-100%)';
        } else {
            // Scrolling up - show navbar
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = scrollTop;
    });
}

/**
 * Lazy loading para imágenes
 */
function addLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback para navegadores sin soporte
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    }
}

/**
 * Mejorar modales para móvil
 */
function enhanceModals() {
    const modals = document.querySelectorAll('.modal, [class*="modal"]');
    
    modals.forEach(modal => {
        // Prevenir scroll del body cuando el modal está abierto
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    if (modal.classList.contains('show') || !modal.classList.contains('hidden')) {
                        document.body.style.overflow = 'hidden';
                    } else {
                        document.body.style.overflow = '';
                    }
                }
            });
        });
        
        observer.observe(modal, { attributes: true });
        
        // Cerrar modal al tocar fuera (solo en móvil)
        if (window.innerWidth <= 768) {
            modal.addEventListener('touchstart', function(e) {
                if (e.target === this) {
                    this.classList.add('hidden');
                    document.body.style.overflow = '';
                }
            });
        }
    });
}

/**
 * Utilidades para desarrolladores
 */
window.MobileEnhancements = {
    isMobile: () => window.innerWidth <= 768,
    isTablet: () => window.innerWidth > 768 && window.innerWidth <= 1024,
    isDesktop: () => window.innerWidth > 1024,
    
    // Función para convertir tabla a cards dinámicamente
    convertTableToCards: function(tableSelector) {
        const table = document.querySelector(tableSelector);
        if (!table) return;
        
        // Implementación de conversión dinámica
        // (se puede expandir según necesidades específicas)
    },
    
    // Función para mostrar toast messages optimizados para móvil
    showToast: function(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#3b82f6'};
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            z-index: 9999;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(-50%) translateY(-20px)';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
};

// Exponer funciones globalmente para uso en templates
window.isMobile = () => window.innerWidth <= 768;
window.showMobileToast = window.MobileEnhancements.showToast;
