/**
 * Sistema SPA Inteligente
 * Decide automaticamente quando fazer navegação SPA vs reload completo
 */

console.log('🧠 SPA Inteligente carregando...');

// Configurações de estruturas de página
const PAGE_STRUCTURES = {
    // Páginas que usam base.html (sem sidebar)
    simple: {
        template: 'base.html',
        routes: ['/', '/demo/', '/icons/'],
        hasHeader: true,
        hasSidebar: false,
        headerType: 'simple'
    },
    
    // Páginas que usam components_base.html (com sidebar)
    components: {
        template: 'components_base.html', 
        routes: ['/components/', '/components/*'],
        hasHeader: true,
        hasSidebar: true,
        headerType: 'components'
    }
};

// Store Alpine.js inteligente
document.addEventListener('alpine:init', () => {
    Alpine.store('spaIntelligent', {
        isLoading: false,
        currentStructure: null,
        
        init() {
            console.log('🧠 Inicializando SPA Inteligente...');
            this.detectCurrentStructure();
            this.setupListeners();
            console.log('✅ SPA Inteligente ativo');
        },
        
        // Detectar estrutura atual da página
        detectCurrentStructure() {
            const path = window.location.pathname;
            const hasSidebar = document.querySelector('[data-spa-sidebar]') !== null;
            
            if (hasSidebar) {
                this.currentStructure = 'components';
                console.log('📄 Estrutura atual: Componentes (com sidebar)');
            } else {
                this.currentStructure = 'simple';
                console.log('📄 Estrutura atual: Simples (sem sidebar)');
            }
        },
        
        // Determinar estrutura necessária para uma rota
        getRequiredStructure(path) {
            if (path.startsWith('/components')) {
                return 'components';
            } else {
                return 'simple';
            }
        },
        
        // Verificar se pode usar SPA (mesma estrutura)
        canUseSPA(targetPath) {
            const requiredStructure = this.getRequiredStructure(targetPath);
            const sameStructure = this.currentStructure === requiredStructure;
            
            console.log(`🔍 Navegação para ${targetPath}:`);
            console.log(`   Estrutura atual: ${this.currentStructure}`);
            console.log(`   Estrutura necessária: ${requiredStructure}`);
            console.log(`   Pode usar SPA: ${sameStructure}`);
            
            return sameStructure;
        },
        
        setupListeners() {
            document.addEventListener('click', (e) => {
                const link = e.target.closest('[data-spa-link]');
                if (!link || link.hasAttribute('data-spa-disabled')) return;
                
                e.preventDefault();
                const targetPath = new URL(link.href).pathname;
                
                this.navigate(targetPath, link.textContent.trim());
            });
        },
        
        async navigate(path, title = '') {
            if (this.isLoading) {
                console.log('🔄 Navegação já em progresso');
                return;
            }
            
            try {
                // Decidir tipo de navegação
                if (this.canUseSPA(path)) {
                    console.log('⚡ Usando navegação SPA');
                    await this.navigateSPA(path, title);
                } else {
                    console.log('🔄 Mudança de estrutura - Reload necessário');
                    this.navigateFullReload(path);
                }
                
            } catch (error) {
                console.error('❌ Erro na navegação:', error);
                this.navigateFullReload(path);
            }
        },
        
        async navigateSPA(path, title) {
            this.isLoading = true;
            this.updateProgressBar(10);
            
            try {
                const url = new URL(path, window.location.origin);
                url.searchParams.set('partial', 'true');
                
                console.log('📡 Requisição SPA:', url.toString());
                this.updateProgressBar(30);
                
                const response = await fetch(url.toString(), {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'application/json'
                    }
                });
                
                this.updateProgressBar(60);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                
                const data = await response.json();
                this.updateProgressBar(80);
                
                // Atualizar conteúdo principal
                const mainContent = document.querySelector('#spa-main-content');
                if (mainContent && data.content) {
                    // Transição suave
                    mainContent.style.opacity = '0.7';
                    await this.sleep(150);
                    
                    mainContent.innerHTML = data.content;
                    
                    // Re-inicializar Alpine.js
                    Alpine.initTree(mainContent);
                    
                    // Atualizar estados ativos
                    this.updateActiveStates(path);
                    
                    // Restaurar opacidade
                    mainContent.style.opacity = '1';
                } else {
                    throw new Error('Conteúdo inválido na resposta');
                }
                
                // Atualizar histórico e título
                if (data.title) {
                    document.title = data.title;
                }
                window.history.pushState({ spa: true, structure: this.currentStructure }, data.title || title, path);
                
                this.updateProgressBar(100);
                console.log('✅ Navegação SPA concluída');
                
            } catch (error) {
                console.error('❌ Erro SPA:', error);
                throw error;
            } finally {
                this.isLoading = false;
                setTimeout(() => this.updateProgressBar(0), 500);
            }
        },
        
        navigateFullReload(path) {
            console.log('🔄 Executando reload completo...');
            
            // Mostrar indicador de carregamento
            this.isLoading = true;
            this.updateProgressBar(50);
            
            // Adicionar classe de loading
            document.body.classList.add('spa-transitioning');
            
            // Pequeno delay para feedback visual
            setTimeout(() => {
                window.location.href = path;
            }, 200);
        },
        
        updateActiveStates(currentPath) {
            // Atualizar links ativos na sidebar
            const sidebarLinks = document.querySelectorAll('[data-spa-sidebar] a');
            sidebarLinks.forEach(link => {
                const linkPath = new URL(link.href).pathname;
                if (linkPath === currentPath) {
                    link.classList.add('bg-accent', 'text-accent-foreground');
                    link.classList.remove('hover:bg-accent');
                } else {
                    link.classList.remove('bg-accent', 'text-accent-foreground');
                    link.classList.add('hover:bg-accent');
                }
            });
            
            // Atualizar links do header
            const headerLinks = document.querySelectorAll('nav a[data-spa-link]');
            headerLinks.forEach(link => {
                const linkPath = new URL(link.href).pathname;
                if (linkPath === currentPath || (currentPath.startsWith('/components') && linkPath === '/components/')) {
                    link.classList.add('text-primary');
                } else {
                    link.classList.remove('text-primary');
                }
            });
        },
        
        updateProgressBar(progress) {
            const progressBar = document.querySelector('#spa-progress-bar');
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
                progressBar.style.opacity = progress > 0 && progress < 100 ? '1' : '0';
            }
        },
        
        sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        },
        
        // Handler para botão voltar/avançar
        handlePopState(event) {
            if (event.state && event.state.spa) {
                const targetStructure = this.getRequiredStructure(window.location.pathname);
                
                if (targetStructure === this.currentStructure) {
                    // Mesma estrutura, pode usar SPA
                    this.navigateSPA(window.location.pathname, document.title);
                } else {
                    // Estrutura diferente, reload necessário
                    window.location.reload();
                }
            }
        }
    });
});

// Inicializar quando Alpine estiver pronto
document.addEventListener('alpine:initialized', () => {
    const spa = Alpine.store('spaIntelligent');
    spa.init();
    
    // Handler para navegação do browser
    window.addEventListener('popstate', (e) => spa.handlePopState(e));
});

// Estilos adicionais
const styles = `
<style>
    .spa-transitioning {
        pointer-events: none;
        opacity: 0.8;
        transition: opacity 0.3s ease;
    }
    
    .spa-transitioning * {
        cursor: wait !important;
    }
    
    #spa-progress-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        z-index: 9999;
        transition: width 0.3s ease, opacity 0.3s ease;
        opacity: 0;
    }
</style>
`;

document.head.insertAdjacentHTML('beforeend', styles);
console.log('✅ SPA Inteligente carregado'); 