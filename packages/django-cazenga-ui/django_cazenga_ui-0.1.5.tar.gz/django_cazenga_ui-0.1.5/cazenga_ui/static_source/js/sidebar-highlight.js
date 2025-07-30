/**
 * Script para corrigir highlight da sidebar automaticamente
 * Funciona tanto para SPA quanto para reload completo
 */

console.log('🎯 Sidebar Highlight Script carregado');

function updateSidebarHighlight() {
    const currentPath = window.location.pathname;
    console.log('📍 Atualizando highlight para:', currentPath);
    
    // Selecionar todos os links da sidebar
    const sidebarLinks = document.querySelectorAll('[data-spa-sidebar] a[data-spa-link]');
    
    sidebarLinks.forEach(link => {
        const linkPath = new URL(link.href).pathname;
        
        // Remover classes ativas
        link.classList.remove('bg-accent', 'text-accent-foreground');
        link.classList.add('hover:bg-accent');
        
        // Aplicar classe ativa se for o caminho atual
        if (linkPath === currentPath) {
            link.classList.add('bg-accent', 'text-accent-foreground');
            link.classList.remove('hover:bg-accent');
            console.log('✅ Highlight aplicado para:', linkPath);
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Iniciando sistema de highlight da sidebar...');
    
    // Aplicar highlight inicial
    setTimeout(updateSidebarHighlight, 100);
    
    // Aplicar highlight após navegação SPA
    window.addEventListener('spa:navigated', (e) => {
        console.log('🔄 SPA navegou, atualizando highlight...');
        setTimeout(updateSidebarHighlight, 150);
    });
    
    // Aplicar highlight após navegação do browser
    window.addEventListener('popstate', () => {
        console.log('↩️ Navegação do browser, atualizando highlight...');
        setTimeout(updateSidebarHighlight, 100);
    });
    
    console.log('✅ Sistema de highlight da sidebar ativo');
});

// Integração com sistema SPA inteligente
document.addEventListener('alpine:initialized', () => {
    if (window.Alpine && window.Alpine.store && window.Alpine.store('spaIntelligent')) {
        console.log('🔗 Integrando com SPA Inteligente...');
        
        // Hook no método navigateSPA para disparar evento
        const spa = window.Alpine.store('spaIntelligent');
        const originalNavigateSPA = spa.navigateSPA;
        
        if (originalNavigateSPA) {
            spa.navigateSPA = async function(path, title) {
                const result = await originalNavigateSPA.call(this, path, title);
                
                // Disparar evento após navegação SPA bem-sucedida
                window.dispatchEvent(new CustomEvent('spa:navigated', {
                    detail: { path: path, title: title }
                }));
                
                return result;
            };
            
            console.log('✅ Integração com SPA Inteligente concluída');
        }
    }
}); 