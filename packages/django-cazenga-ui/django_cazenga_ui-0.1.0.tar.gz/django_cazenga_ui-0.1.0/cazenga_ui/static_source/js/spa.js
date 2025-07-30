/**
 * Sistema SPA para Django Tailwind Alpine
 * Gerencia navegação sem recarregar a página inteira
 */

// Store Alpine.js para gerenciar estado SPA
document.addEventListener('alpine:init', () => {
    Alpine.store('spa', {
        // Estado
        isLoading: false,
        currentPath: window.location.pathname,
        currentTitle: document.title,
        loadingProgress: 0,
        
        // Configurações
        config: {
            mainContentSelector: '#spa-main-content',
            sidebarSelector: '[data-spa-sidebar]',
            headerSelector: '[data-spa-header]',
            contentPartialParam: 'partial',
            animationDuration: 300,
            enableProgressBar: true,
            enableTransitions: true,
        },
        
        // Inicializar SPA
        init() {
            this.setupEventListeners();
            this.setupPopStateHandler();
            this.initializeSidebarLinks();
            console.log('🚀 SPA initialized');
        },
        
        // Configurar event listeners
        setupEventListeners() {
            // Interceptar cliques em links SPA
            document.addEventListener('click', (e) => {
                const link = e.target.closest('[data-spa-link]');
                if (link && !link.hasAttribute('data-spa-disabled')) {
                    e.preventDefault();
                    this.navigate(link.getAttribute('href'), {
                        title: link.getAttribute('data-spa-title') || link.textContent.trim(),
                        addToHistory: true,
                    });
                }
            });
            
            // Interceptar submit de formulários SPA
            document.addEventListener('submit', (e) => {
                const form = e.target.closest('[data-spa-form]');
                if (form) {
                    e.preventDefault();
                    this.submitForm(form);
                }
            });
        },
        
        // Configurar handler para botão voltar/avançar
        setupPopStateHandler() {
            window.addEventListener('popstate', (e) => {
                if (e.state && e.state.spaRoute) {
                    this.navigate(e.state.spaRoute.path, {
                        title: e.state.spaRoute.title,
                        addToHistory: false,
                        fromPopState: true,
                    });
                }
            });
            
            // Adicionar estado inicial ao histórico
            if (!window.history.state || !window.history.state.spaRoute) {
                window.history.replaceState({
                    spaRoute: {
                        path: window.location.pathname,
                        title: document.title,
                    }
                }, document.title, window.location.pathname);
            }
        },
        
        // Inicializar links da sidebar
        initializeSidebarLinks() {
            const sidebarLinks = document.querySelectorAll('[data-spa-sidebar] a');
            sidebarLinks.forEach(link => {
                if (!link.hasAttribute('data-spa-link')) {
                    link.setAttribute('data-spa-link', '');
                }
            });
        },
        
        // Navegar para nova rota
        async navigate(path, options = {}) {
            const {
                title = '',
                addToHistory = true,
                fromPopState = false,
                method = 'GET',
                data = null,
            } = options;
            
            // Prevenir navegação se já estiver carregando
            if (this.isLoading) {
                console.log('🔄 Navigation already in progress');
                return;
            }
            
            // Prevenir navegação para a mesma rota
            if (path === this.currentPath && !data) {
                console.log('🔄 Already on this route');
                return;
            }
            
            try {
                this.setLoading(true);
                this.updateProgress(10);
                
                // Construir URL com parâmetro para conteúdo parcial
                const url = new URL(path, window.location.origin);
                if (method === 'GET') {
                    url.searchParams.set(this.config.contentPartialParam, 'true');
                }
                
                this.updateProgress(30);
                
                // Fazer requisição AJAX
                const response = await fetch(url.toString(), {
                    method: method,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json',
                        ...(method === 'POST' && { 'X-CSRFToken': this.getCSRFToken() }),
                    },
                    body: data ? JSON.stringify(data) : null,
                });
                
                this.updateProgress(60);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                this.updateProgress(80);
                
                // Atualizar conteúdo
                await this.updateContent(result);
                
                // Atualizar estado
                this.currentPath = path;
                this.currentTitle = title || result.title || document.title;
                
                // Atualizar histórico do navegador
                if (addToHistory && !fromPopState) {
                    window.history.pushState({
                        spaRoute: {
                            path: path,
                            title: this.currentTitle,
                        }
                    }, this.currentTitle, path);
                }
                
                // Atualizar título da página
                if (this.currentTitle) {
                    document.title = this.currentTitle;
                }
                
                // Scroll para o topo
                window.scrollTo({ top: 0, behavior: 'smooth' });
                
                this.updateProgress(100);
                
                // Dispatch evento personalizado
                this.dispatchNavigationEvent('spa:navigated', {
                    path: path,
                    title: this.currentTitle,
                    fromPopState: fromPopState,
                });
                
                console.log(`✅ Navigated to: ${path}`);
                
            } catch (error) {
                console.error('❌ Navigation error:', error);
                this.handleNavigationError(error, path);
            } finally {
                this.setLoading(false);
                this.updateProgress(0);
            }
        },
        
        // Atualizar conteúdo da página
        async updateContent(result) {
            const mainContent = document.querySelector(this.config.mainContentSelector);
            if (!mainContent) {
                throw new Error('Main content element not found');
            }
            
            // Aplicar transição de saída se habilitada
            if (this.config.enableTransitions) {
                mainContent.style.opacity = '0';
                mainContent.style.transform = 'translateY(10px)';
                await this.sleep(150);
            }
            
            // Atualizar conteúdo
            mainContent.innerHTML = result.content || result.main_content || '';
            
            // Atualizar sidebar se fornecida
            if (result.sidebar_content) {
                const sidebar = document.querySelector(this.config.sidebarSelector);
                if (sidebar) {
                    sidebar.innerHTML = result.sidebar_content;
                    this.initializeSidebarLinks();
                }
            }
            
            // Atualizar header se fornecido
            if (result.header_content) {
                const header = document.querySelector(this.config.headerSelector);
                if (header) {
                    header.innerHTML = result.header_content;
                }
            }
            
            // Re-inicializar Alpine.js nos novos elementos
            Alpine.initTree(mainContent);
            
            // Aplicar transição de entrada se habilitada
            if (this.config.enableTransitions) {
                await this.sleep(50);
                mainContent.style.opacity = '1';
                mainContent.style.transform = 'translateY(0)';
            }
        },
        
        // Submeter formulário via AJAX
        async submitForm(form) {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            await this.navigate(form.action, {
                method: form.method.toUpperCase(),
                data: data,
                addToHistory: form.hasAttribute('data-spa-history'),
            });
        },
        
        // Definir estado de loading
        setLoading(loading) {
            this.isLoading = loading;
            document.body.classList.toggle('spa-loading', loading);
            
            // Dispatch evento de loading
            this.dispatchNavigationEvent('spa:loading', { loading });
        },
        
        // Atualizar progress bar
        updateProgress(progress) {
            this.loadingProgress = progress;
            
            if (this.config.enableProgressBar) {
                const progressBar = document.querySelector('#spa-progress-bar');
                if (progressBar) {
                    progressBar.style.width = `${progress}%`;
                    progressBar.style.opacity = progress > 0 && progress < 100 ? '1' : '0';
                }
            }
        },
        
        // Tratar erro de navegação
        handleNavigationError(error, path) {
            console.error('Navigation failed:', error);
            
            // Dispatch evento de erro
            this.dispatchNavigationEvent('spa:error', { error, path });
            
            // Fallback: navegar normalmente
            if (confirm('Houve um erro ao carregar a página. Deseja tentar novamente?')) {
                window.location.href = path;
            }
        },
        
        // Dispatch evento personalizado
        dispatchNavigationEvent(eventName, detail) {
            window.dispatchEvent(new CustomEvent(eventName, {
                detail: detail,
                bubbles: true,
            }));
        },
        
        // Utilitários
        sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        },
        
        getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        },
        
        // Recarregar página atual
        refresh() {
            this.navigate(this.currentPath, {
                title: this.currentTitle,
                addToHistory: false,
            });
        },
        
        // Verificar se uma rota está ativa
        isActive(path) {
            return this.currentPath === path;
        },
    });
});

// Inicializar SPA quando Alpine.js estiver pronto
document.addEventListener('alpine:initialized', () => {
    Alpine.store('spa').init();
});

// Estilos CSS para transições SPA
const spaStyles = `
    <style>
        /* Loading state */
        .spa-loading {
            cursor: wait;
        }
        
        /* Progress bar */
        #spa-progress-bar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background-color: hsl(var(--primary));
            z-index: 9999;
            transition: width 0.3s ease, opacity 0.3s ease;
            opacity: 0;
        }
        
        /* Transições de conteúdo */
        #spa-main-content {
            transition: opacity 0.3s ease, transform 0.3s ease;
        }
        
        /* Link ativo */
        [data-spa-link].spa-active {
            background-color: hsl(var(--accent));
            color: hsl(var(--accent-foreground));
        }
        
        /* Link desabilitado */
        [data-spa-link][data-spa-disabled] {
            pointer-events: none;
            opacity: 0.5;
        }
        
        /* Loading spinner */
        .spa-loading-spinner {
            display: inline-block;
            width: 1rem;
            height: 1rem;
            border: 2px solid hsl(var(--muted));
            border-radius: 50%;
            border-top-color: hsl(var(--primary));
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Fade in animation */
        .spa-fade-in {
            animation: spaFadeIn 0.3s ease;
        }
        
        @keyframes spaFadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
`;

// Inserir estilos na página
document.head.insertAdjacentHTML('beforeend', spaStyles); 