// Portal NODO - Efectos Avanzados

class PortalEffects {
    constructor() {
        this.init();
    }

    init() {
        this.setupParticles();
        this.setupScrollEffects();
        this.setupHoverEffects();
        this.setupLoadingStates();
        this.setupTooltips();
    }

    // Sistema de partículas de fondo
    setupParticles() {
        const canvas = document.createElement('canvas');
        canvas.id = 'particles-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '-1';
        canvas.style.opacity = '0.6';
        
        document.body.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        let particles = [];
        
        const resizeCanvas = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };
        
        const createParticle = () => ({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            size: Math.random() * 3 + 1,
            speedX: (Math.random() - 0.5) * 0.5,
            speedY: (Math.random() - 0.5) * 0.5,
            opacity: Math.random() * 0.8 + 0.4,
            color: `hsl(${Math.random() * 60 + 200}, 70%, 60%)`
        });
        
        const initParticles = () => {
            particles = [];
            for (let i = 0; i < 80; i++) {
                particles.push(createParticle());
            }
        };
        
        const updateParticles = () => {
            particles.forEach(particle => {
                particle.x += particle.speedX;
                particle.y += particle.speedY;
                
                if (particle.x < 0 || particle.x > canvas.width) particle.speedX *= -1;
                if (particle.y < 0 || particle.y > canvas.height) particle.speedY *= -1;
            });
        };
        
        const drawParticles = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            particles.forEach(particle => {
                ctx.beginPath();
                ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
                ctx.fillStyle = particle.color;
                ctx.globalAlpha = particle.opacity;
                ctx.fill();
            });
            
            // Conectar partículas cercanas
            particles.forEach((particle, i) => {
                particles.slice(i + 1).forEach(otherParticle => {
                    const distance = Math.sqrt(
                        Math.pow(particle.x - otherParticle.x, 2) +
                        Math.pow(particle.y - otherParticle.y, 2)
                    );
                    
                    if (distance < 100) {
                        ctx.beginPath();
                        ctx.moveTo(particle.x, particle.y);
                        ctx.lineTo(otherParticle.x, otherParticle.y);
                        ctx.strokeStyle = particle.color;
                        ctx.globalAlpha = (100 - distance) / 100 * 0.4;
                        ctx.lineWidth = 1;
                        ctx.stroke();
                    }
                });
            });
        };
        
        const animate = () => {
            updateParticles();
            drawParticles();
            requestAnimationFrame(animate);
        };
        
        resizeCanvas();
        initParticles();
        animate();
        
        window.addEventListener('resize', () => {
            resizeCanvas();
            initParticles();
        });
    }

    // Efectos de scroll avanzados
    setupScrollEffects() {
        let ticking = false;
        
        const updateScrollEffects = () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            
            // Parallax para elementos de fondo
            document.querySelectorAll('.parallax-bg').forEach(element => {
                element.style.transform = `translateY(${rate}px)`;
            });
            
            // Efecto de revelado progresivo
            document.querySelectorAll('.reveal-on-scroll').forEach(element => {
                const elementTop = element.offsetTop;
                const elementHeight = element.offsetHeight;
                const windowHeight = window.innerHeight;
                
                if (scrolled > elementTop - windowHeight + elementHeight / 4) {
                    element.classList.add('revealed');
                }
            });
            
            ticking = false;
        };
        
        const requestScrollUpdate = () => {
            if (!ticking) {
                requestAnimationFrame(updateScrollEffects);
                ticking = true;
            }
        };
        
        window.addEventListener('scroll', requestScrollUpdate);
    }

    // Efectos de hover mejorados
    setupHoverEffects() {
        document.querySelectorAll('.card-hover').forEach(card => {
            card.addEventListener('mouseenter', (e) => {
                const rect = e.target.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                e.target.style.setProperty('--mouse-x', `${x}px`);
                e.target.style.setProperty('--mouse-y', `${y}px`);
                
                // Agregar efecto de brillo
                const shine = document.createElement('div');
                shine.className = 'absolute inset-0 opacity-0 transition-opacity duration-300 pointer-events-none';
                shine.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(255,255,255,0.1) 0%, transparent 50%)`;
                
                e.target.style.position = 'relative';
                e.target.appendChild(shine);
                
                setTimeout(() => {
                    shine.style.opacity = '1';
                }, 10);
            });
            
            card.addEventListener('mouseleave', (e) => {
                const shines = e.target.querySelectorAll('.absolute.inset-0');
                shines.forEach(shine => {
                    shine.style.opacity = '0';
                    setTimeout(() => {
                        if (shine.parentNode) {
                            shine.parentNode.removeChild(shine);
                        }
                    }, 300);
                });
            });
        });
    }

    // Estados de carga mejorados
    setupLoadingStates() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Procesando...';
                    
                    // Agregar barra de progreso
                    const progressBar = document.createElement('div');
                    progressBar.className = 'w-full bg-gray-200 rounded-full h-1 mt-2';
                    progressBar.innerHTML = '<div class="bg-blue-600 h-1 rounded-full transition-all duration-1000" style="width: 0%"></div>';
                    
                    submitButton.parentNode.appendChild(progressBar);
                    
                    // Simular progreso
                    setTimeout(() => {
                        progressBar.querySelector('div').style.width = '100%';
                    }, 100);
                }
            });
        });
    }

    // Sistema de tooltips
    setupTooltips() {
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            const tooltip = document.createElement('div');
            tooltip.className = 'absolute z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg opacity-0 pointer-events-none transition-all duration-200 transform -translate-y-2';
            tooltip.textContent = element.getAttribute('data-tooltip');
            
            element.style.position = 'relative';
            element.appendChild(tooltip);
            
            element.addEventListener('mouseenter', () => {
                tooltip.style.opacity = '1';
                tooltip.style.transform = 'translateY(-100%) translateX(-50%)';
                tooltip.style.left = '50%';
                tooltip.style.bottom = '100%';
                tooltip.style.marginBottom = '5px';
            });
            
            element.addEventListener('mouseleave', () => {
                tooltip.style.opacity = '0';
                tooltip.style.transform = 'translateY(-100%) translateX(-50%) translateY(-10px)';
            });
        });
    }

    // Método para agregar efectos de typing
    static typeWriter(element, text, speed = 50) {
        let i = 0;
        element.innerHTML = '';
        
        const type = () => {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        };
        
        type();
    }

    // Método para crear notificaciones toast
    static showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-lg shadow-lg text-white transform translate-x-full transition-transform duration-300`;
        
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };
        
        toast.classList.add(colors[type] || colors.info);
        toast.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'times' : type === 'warning' ? 'exclamation' : 'info'}-circle mr-3"></i>
                <span>${message}</span>
                <button class="ml-4 text-white hover:text-gray-200" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Mostrar toast
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 100);
        
        // Ocultar automáticamente
        setTimeout(() => {
            toast.style.transform = 'translateX(full)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
    }
}

// Inicializar efectos cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new PortalEffects();
    
    // Agregar clases CSS dinámicamente
    const style = document.createElement('style');
    style.textContent = `
        .revealed {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
        
        .reveal-on-scroll {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.6s ease-out;
        }
        
        .parallax-bg {
            will-change: transform;
        }
    `;
    document.head.appendChild(style);
});

// Exportar para uso global
window.PortalEffects = PortalEffects;
