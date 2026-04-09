// Persistencia de solapa activa en programa ÑACHEC
document.addEventListener('DOMContentLoaded', function() {
    const STORAGE_KEY = 'nachec_active_tab';
    
    // Restaurar solapa activa al cargar
    const savedTab = localStorage.getItem(STORAGE_KEY);
    if (savedTab) {
        const tabLink = document.querySelector(`a[data-solapa="${savedTab}"]`);
        if (tabLink && !tabLink.classList.contains('solapa-activa')) {
            window.location.href = tabLink.href;
        }
    }
    
    // Guardar solapa al hacer clic
    document.querySelectorAll('.solapa-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const solapaId = this.getAttribute('data-solapa');
            if (solapaId) {
                localStorage.setItem(STORAGE_KEY, solapaId);
            }
        });
    });
});
