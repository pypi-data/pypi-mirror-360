/**
 * Script de Debug para o Sistema SPA
 */

// Verificar se Alpine.js está carregado
console.log('🔍 DEBUG SPA - Verificando carregamento...');
console.log('Alpine.js disponível:', typeof Alpine !== 'undefined');

// Verificar se o script SPA principal foi carregado
document.addEventListener('alpine:init', () => {
    console.log('🟢 Alpine.js inicializado');
    
    // Verificar se o store SPA existe
    if (Alpine.store('spa')) {
        console.log('✅ Store SPA encontrado:', Alpine.store('spa'));
    } else {
        console.error('❌ Store SPA NÃO encontrado! Problema no carregamento do spa.js');
    }
});

document.addEventListener('alpine:initialized', () => {
    console.log('🟢 Alpine.js completamente inicializado');
    
    // Verificar elementos SPA
    const mainContent = document.querySelector('#spa-main-content');
    const spaLinks = document.querySelectorAll('[data-spa-link]');
    const sidebar = document.querySelector('[data-spa-sidebar]');
    
    console.log('🔍 Elementos SPA encontrados:');
    console.log('- Main content:', mainContent ? '✅' : '❌', mainContent);
    console.log('- Links SPA:', spaLinks.length, spaLinks);
    console.log('- Sidebar:', sidebar ? '✅' : '❌', sidebar);
    
    // Adicionar listeners de debug nos links
    spaLinks.forEach((link, index) => {
        link.addEventListener('click', (e) => {
            console.log(`🖱️ Clique no link SPA ${index + 1}:`, link.href);
            
            // Verificar se o SPA vai interceptar
            if (Alpine.store('spa') && !link.hasAttribute('data-spa-disabled')) {
                console.log('✅ Link será interceptado pelo SPA');
            } else {
                console.log('⚠️ Link NÃO será interceptado');
            }
        });
    });
    
    // Eventos SPA customizados
    window.addEventListener('spa:loading', (e) => {
        console.log('🔄 SPA Loading:', e.detail);
    });
    
    window.addEventListener('spa:navigated', (e) => {
        console.log('✅ SPA Navegação completa:', e.detail);
    });
    
    window.addEventListener('spa:error', (e) => {
        console.error('❌ Erro SPA:', e.detail);
    });
});

// Debug de requisições AJAX
const originalFetch = window.fetch;
window.fetch = function(...args) {
    const url = args[0];
    console.log('🌐 Requisição AJAX:', url);
    
    return originalFetch.apply(this, args).then(response => {
        console.log('📥 Resposta AJAX:', response.status, response.url);
        return response;
    }).catch(error => {
        console.error('❌ Erro AJAX:', error);
        throw error;
    });
};

// Verificar se o arquivo spa.js foi carregado
const spaScript = document.querySelector('script[src*="spa.js"]');
if (spaScript) {
    console.log('✅ Script spa.js encontrado no DOM');
    
    // Verificar se o arquivo existe
    fetch(spaScript.src)
        .then(response => {
            if (response.ok) {
                console.log('✅ Arquivo spa.js carregado com sucesso');
            } else {
                console.error('❌ Erro ao carregar spa.js:', response.status);
            }
        })
        .catch(error => {
            console.error('❌ Erro de rede ao carregar spa.js:', error);
        });
} else {
    console.error('❌ Script spa.js NÃO encontrado no DOM');
}

console.log('🔍 DEBUG SPA - Inicialização completa'); 