/**
 * Versão Simplificada do Sistema SPA para Debug
 */

console.log('🚀 SPA Simples carregando...');

// Store Alpine.js simples
document.addEventListener('alpine:init', () => {
    console.log('🟢 Inicializando store SPA simples...');
    
    Alpine.store('spaSimple', {
        isLoading: false,
        
        init() {
            console.log('✅ SPA Simples inicializado');
            this.setupListeners();
        },
        
        setupListeners() {
            console.log('🔧 Configurando listeners...');
            
            // Interceptar todos os cliques em links com data-spa-link
            document.addEventListener('click', (e) => {
                const link = e.target.closest('[data-spa-link]');
                
                if (link) {
                    console.log('🖱️ Clique interceptado no link:', link.href);
                    e.preventDefault();
                    
                    this.navigate(link.href);
                }
            });
        },
        
        async navigate(url) {
            console.log('🔄 Navegando para:', url);
            this.isLoading = true;
            
            try {
                // Adicionar parâmetro para requisição parcial
                const fetchUrl = new URL(url);
                fetchUrl.searchParams.set('partial', 'true');
                
                console.log('📡 Fazendo requisição AJAX:', fetchUrl.toString());
                
                const response = await fetch(fetchUrl.toString(), {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                
                const data = await response.json();
                console.log('📥 Dados recebidos:', data);
                
                // Atualizar conteúdo principal
                const mainContent = document.querySelector('#spa-main-content');
                if (mainContent && data.content) {
                    console.log('🔄 Atualizando conteúdo principal...');
                    mainContent.innerHTML = data.content;
                    
                    // Re-inicializar Alpine.js no novo conteúdo
                    Alpine.initTree(mainContent);
                }
                
                // Atualizar URL
                if (data.title) {
                    document.title = data.title;
                }
                window.history.pushState({}, data.title || '', url);
                
                console.log('✅ Navegação SPA concluída!');
                
            } catch (error) {
                console.error('❌ Erro na navegação SPA:', error);
                console.log('🔄 Fallback: navegação normal');
                window.location.href = url;
            } finally {
                this.isLoading = false;
            }
        }
    });
});

// Inicializar quando Alpine estiver pronto
document.addEventListener('alpine:initialized', () => {
    console.log('🟢 Alpine inicializado, ativando SPA...');
    Alpine.store('spaSimple').init();
});

console.log('✅ SPA Simples carregado'); 