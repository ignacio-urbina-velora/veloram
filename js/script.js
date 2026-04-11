console.log('%c🚀 Proyecto funcionando!', 'color: #10b981; font-size: 20px; font-weight: bold;');

document.addEventListener('DOMContentLoaded', function() {
    console.log('%c✅ DOM cargado', 'color: #10b981; font-weight: bold;');
    
    // Select all links and add logic
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', e => {
            const href = link.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                console.log('%cLink clickeado (Ancla):', 'color: #6366f1;', href);
                
                const targetId = href.substring(1);
                const element = document.getElementById(targetId);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth' });
                }
            } else {
                console.log('%cLink clickeado:', 'color: #6366f1;', link.href);
            }
        });
    });
});
