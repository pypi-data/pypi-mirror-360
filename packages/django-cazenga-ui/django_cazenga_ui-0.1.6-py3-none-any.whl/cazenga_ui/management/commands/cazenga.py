"""
Comando Cazenga para Django Cazenga UI
Comando principal para inicialização e configuração do projeto
"""

import os
import shutil
import subprocess
import sys
import re
from pathlib import Path
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    """Comando principal para Django Cazenga UI"""
    
    help = 'Inicializa e configura Django Cazenga UI no projeto'
    
    # Nome da app que será criada pelo django-tailwind (diferente da biblioteca cazenga_ui)
    TAILWIND_APP_NAME = 'theme'
    
    # Temas disponíveis
    THEMES = {
        'default': {
            'name': 'Default',
            'description': 'Neutral default theme',
            'primary': '#3b82f6',
            'secondary': '#64748b',
        },
        'blue': {
            'name': 'Blue',
            'description': 'Classic theme in blue tones',
            'primary': '#2563eb',
            'secondary': '#1e40af',
        },
        'orange': {
            'name': 'Orange',
            'description': 'Energetic theme in orange tones',
            'primary': '#ea580c',
            'secondary': '#dc2626',
        },
        'green': {
            'name': 'Green',
            'description': 'Natural theme in green tones',
            'primary': '#059669',
            'secondary': '#047857',
        },
        'roxo': {
            'name': 'Violet',
            'description': 'Modern theme in violet tones',
            'primary': '#7c3aed',
            'secondary': '#6d28d9',
        },
        'red': {
            'name': 'Red',
            'description': 'Vibrant theme in red tones',
            'primary': '#dc2626',
            'secondary': '#b91c1c',
        },
        'yellow': {
            'name': 'Yellow',
            'description': 'Cheerful theme in yellow tones',
            'primary': '#d97706',
            'secondary': '#b45309',
        },
        'rose': {
            'name': 'Rose',
            'description': 'Elegant theme in rose tones',
            'primary': '#e11d48',
            'secondary': '#be185d',
        },
    }
    
    def add_arguments(self, parser):
        """Adiciona argumentos ao comando"""
        subparsers = parser.add_subparsers(dest='action', help='Ações disponíveis')
        
        # Subcomando: init
        init_parser = subparsers.add_parser('init', help='Inicializa o projeto')
        init_parser.add_argument(
            '--theme',
            type=str,
            choices=list(self.THEMES.keys()),
            help='Tema de cores a ser usado'
        )
        init_parser.add_argument(
            '--with-tailwind',
            action='store_true',
            help='Configura e instala django-tailwind automaticamente'
        )
        init_parser.add_argument(
            '--skip-npm',
            action='store_true',
            help='Pula instalação de dependências npm'
        )
        
        # Subcomando: themes
        themes_parser = subparsers.add_parser('themes', help='Lista temas disponíveis')
        
        # Subcomando: switch-theme
        switch_parser = subparsers.add_parser('switch-theme', help='Altera tema do projeto')
        switch_parser.add_argument(
            'theme',
            type=str,
            choices=list(self.THEMES.keys()),
            help='Novo tema a ser aplicado'
        )
        
        # Subcomando: status
        status_parser = subparsers.add_parser('status', help='Mostra status da configuração')
    
    def handle(self, *args, **options):
        """Processa o comando"""
        action = options['action']
        
        if action == 'init':
            self.handle_init(options)
        elif action == 'themes':
            self.handle_themes()
        elif action == 'switch-theme':
            self.handle_switch_theme(options)
        elif action == 'status':
            self.handle_status()
        else:
            self.print_help()
    
    def handle_init(self, options):
        """Inicializa o projeto"""
        self.stdout.write(
            self.style.SUCCESS('\n🎨 Inicializando Django Cazenga UI...\n')
        )
        
        # Configurar django-tailwind se solicitado
        with_tailwind = options.get('with_tailwind', False)
        skip_npm = options.get('skip_npm', False)
        
        if with_tailwind:
            if not self._setup_tailwind(skip_npm):
                self.stdout.write(
                    self.style.ERROR('❌ Falha na configuração do django-tailwind. Abortando...')
                )
                return
        else:
            # Verifica se django-tailwind já está configurado
            if not self._has_tailwind_app():
                self.stdout.write(
                    self.style.ERROR(f'❌ App {self.TAILWIND_APP_NAME} não encontrada.')
                )
                self.stdout.write('💡 Execute com --with-tailwind ou configure django-tailwind primeiro:')
                self.stdout.write(f'   python manage.py tailwind init {self.TAILWIND_APP_NAME}')
                self.stdout.write('   python manage.py tailwind install')
                return
        
        # Escolher tema
        theme = options.get('theme')
        if not theme:
            theme = self._choose_theme()
        
        # Integrar com estrutura existente do django-tailwind
        self._integrate_with_tailwind(theme)
        
        # Próximos passos
        self._show_success_message(theme, with_tailwind)
    
    def handle_themes(self):
        """Lista temas disponíveis"""
        self.stdout.write(
            self.style.SUCCESS('\n🎨 Temas disponíveis:\n')
        )
        
        for key, theme in self.THEMES.items():
            self.stdout.write(f'  {key:<10} - {theme["name"]:<10} ({theme["description"]})')
        
        self.stdout.write(f'\n  Total: {len(self.THEMES)} temas')
    
    def handle_switch_theme(self, options):
        """Altera tema do projeto"""
        theme = options['theme']
        
        if not self._has_tailwind_app():
            raise CommandError(
                f'App {self.TAILWIND_APP_NAME} não encontrada. Execute "python manage.py cazenga init --with-tailwind" primeiro.'
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎨 Alterando tema para "{self.THEMES[theme]["name"]}"...\n')
        )
        
        # Substituir tema
        self._setup_theme(theme)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Tema alterado para "{self.THEMES[theme]["name"]}"')
        )
        
        # Mostrar próximos passos
        self.stdout.write('\n📋 Próximos passos:')
        self.stdout.write('   1. Execute: python manage.py tailwind build')
        self.stdout.write('   2. Para desenvolvimento: python manage.py tailwind start')
        self.stdout.write('   3. Recarregue sua aplicação para ver o novo tema')
    
    def handle_status(self):
        """Mostra status da configuração"""
        self.stdout.write(
            self.style.SUCCESS('\n📊 Status da configuração:\n')
        )
        
        base_dir = Path(settings.BASE_DIR)
        has_tailwind = self._has_tailwind_app()
        
        if has_tailwind:
            # Verifica estrutura django-tailwind
            checks = [
                (f'App {self.TAILWIND_APP_NAME}', base_dir / self.TAILWIND_APP_NAME),
                ('Diretório static_src', base_dir / self.TAILWIND_APP_NAME / 'static_src'),
                ('Package.json', base_dir / self.TAILWIND_APP_NAME / 'static_src' / 'package.json'),
                ('PostCSS config', base_dir / self.TAILWIND_APP_NAME / 'static_src' / 'postcss.config.js'),
                ('Styles.css fonte', base_dir / self.TAILWIND_APP_NAME / 'static_src' / 'src' / 'styles.css'),
                ('Components.css', base_dir / self.TAILWIND_APP_NAME / 'static_src' / 'src' / 'components.css'),
                ('CSS compilado', base_dir / self.TAILWIND_APP_NAME / 'static' / 'css' / 'dist' / 'styles.css'),
                ('Template base', base_dir / self.TAILWIND_APP_NAME / 'templates' / 'base.html'),
                ('Componentes UI', base_dir / self.TAILWIND_APP_NAME / 'templates' / 'components' / 'ui'),
                ('Componentes Layout', base_dir / self.TAILWIND_APP_NAME / 'templates' / 'components' / 'layout'),
                ('JavaScript', base_dir / self.TAILWIND_APP_NAME / 'static' / 'js'),
                ('Ícones', base_dir / self.TAILWIND_APP_NAME / 'static' / 'icons'),
            ]
        else:
            self.stdout.write('  ❌ Django-tailwind não configurado')
            self.stdout.write('  💡 Execute: python manage.py cazenga init --with-tailwind')
            return
        
        for name, path in checks:
            status = "✅" if path.exists() else "❌"
            self.stdout.write(f'  {status} {name}')
        
        # Verifica configurações
        self._check_dependencies_status()
        
        # Verifica tema atual
        current_theme = self._get_current_theme()
        if current_theme:
            self.stdout.write(f'  🎨 Tema atual: {current_theme}')
        else:
            self.stdout.write('  ❌ Tema não identificado')
    
    def _has_tailwind_app(self) -> bool:
        """Verifica se a app theme (django-tailwind) existe e está configurada"""
        base_dir = Path(settings.BASE_DIR)
        tailwind_app_path = base_dir / self.TAILWIND_APP_NAME
        static_src_path = tailwind_app_path / 'static_src'
        
        return tailwind_app_path.exists() and static_src_path.exists()
    
    def _check_nodejs(self) -> bool:
        """Verifica se Node.js está instalado"""
        try:
            # Verifica node --version
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.stdout.write(f'  ✅ Node.js encontrado: {result.stdout.strip()}')
                return True
            else:
                return False
        except FileNotFoundError:
            return False
        except Exception:
            return False
    
    def _check_installed_apps(self) -> dict:
        """Verifica quais apps necessárias estão no INSTALLED_APPS"""
        required_apps = {
            'tailwind': False,
            'cazenga_ui': False,
            'django_browser_reload': False,
            'mathfilters': False,
        }
        
        installed_apps = getattr(settings, 'INSTALLED_APPS', [])
        
        for app in required_apps:
            required_apps[app] = app in installed_apps
            
        return required_apps
    
    def _setup_tailwind(self, skip_npm: bool = False) -> bool:
        """Configura django-tailwind do zero"""
        self.stdout.write('🔧 Configurando django-tailwind...')
        
        # Verifica se django-tailwind está instalado
        try:
            import tailwind
            tailwind_installed = True
        except ImportError:
            tailwind_installed = False
        
        # Verifica se as apps estão no INSTALLED_APPS
        installed_apps_status = self._check_installed_apps()
        
        # Se django-tailwind está instalado mas não no INSTALLED_APPS
        if tailwind_installed and not installed_apps_status['tailwind']:
            self.stdout.write(
                self.style.ERROR('  ❌ Django-tailwind está instalado mas não configurado no settings.py')
            )
            self.stdout.write('')
            self.stdout.write('  🔧 Configuração necessária em settings.py:')
            self.stdout.write('')
            self.stdout.write('  INSTALLED_APPS += [')
            
            if not installed_apps_status['tailwind']:
                self.stdout.write("      'tailwind',")
            if not installed_apps_status['cazenga_ui']:
                self.stdout.write("      'cazenga_ui',")
            if not installed_apps_status['django_browser_reload']:
                self.stdout.write("      'django_browser_reload',")
            if not installed_apps_status['mathfilters']:
                self.stdout.write("      'mathfilters',")
                
            self.stdout.write('  ]')
            self.stdout.write('')
            self.stdout.write('  MIDDLEWARE += [')
            self.stdout.write("      'django_browser_reload.middleware.BrowserReloadMiddleware',")
            self.stdout.write('  ]')
            self.stdout.write('')
            self.stdout.write(f"  TAILWIND_APP_NAME = '{self.TAILWIND_APP_NAME}'")
            self.stdout.write('  NPM_BIN_PATH = r"C:\\Program Files\\nodejs\\npm.cmd"  # Windows')
            self.stdout.write('')
            self.stdout.write('  💡 Depois de configurar, execute novamente:')
            self.stdout.write('     python manage.py cazenga init --with-tailwind')
            return False
        
        # Se django-tailwind não está instalado
        if not tailwind_installed:
            self.stdout.write(
                self.style.ERROR('  ❌ django-tailwind não está instalado.')
            )
            self.stdout.write('  💡 Instale com: pip install django-cazenga-ui')
            return False
        
        # Verifica se Node.js está instalado (se não for pular npm)
        if not skip_npm:
            if not self._check_nodejs():
                self.stdout.write(
                    self.style.ERROR('  ❌ Node.js não está instalado ou não foi encontrado.')
                )
                self.stdout.write('  💡 Instale Node.js: https://nodejs.org')
                self.stdout.write('  💡 Ou execute com --skip-npm e instale manualmente depois')
                return False
        
        # Verifica se já está configurado
        if self._has_tailwind_app():
            self.stdout.write(f'  ✅ App {self.TAILWIND_APP_NAME} já existe e está configurada')
            # NÃO retorna aqui - continua para garantir configuração completa
        else:
            # Cria a app se não existir
            base_dir = Path(settings.BASE_DIR)
            
            try:
                # 1. Executar tailwind init {self.TAILWIND_APP_NAME}
                self.stdout.write(f'  🏗️ Criando app {self.TAILWIND_APP_NAME}...')
                
                # Tentar primeiro abordagem simples com timeout
                try:
                    # Debug: comando sendo executado
                    cmd = [sys.executable, 'manage.py', 'tailwind', 'init']
                    self.stdout.write(f'  📋 Executando: {" ".join(cmd)}')
                    
                    process = subprocess.Popen(
                        cmd,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=base_dir,
                        text=True
                    )
                    
                    # Enviar respostas para as duas perguntas do tailwind init
                    self.stdout.write(f'  📤 Configurando app: {self.TAILWIND_APP_NAME}')
                    self.stdout.write(f'  📤 DaisyUI: Não incluir')
                    
                    # Tentar com timeout
                    try:
                        # Enviar DUAS respostas: nome da app + resposta daisyUI
                        input_data = f'{self.TAILWIND_APP_NAME}\n1\n'
                        stdout, stderr = process.communicate(input=input_data, timeout=30)
                    except subprocess.TimeoutExpired:
                        self.stdout.write('  ⏱️ Timeout na execução automática')
                        process.kill()
                        stdout, stderr = process.communicate()
                        
                        # Fallback para modo manual
                        self.stdout.write('')
                        self.stdout.write('  🔄 Modo automático falhou. Vamos tentar modo manual:')
                        self.stdout.write('  📋 Execute manualmente:')
                        self.stdout.write('     python manage.py tailwind init')
                        self.stdout.write(f'     (quando perguntar o nome, digite: {self.TAILWIND_APP_NAME})')
                        self.stdout.write('     (quando perguntar sobre daisyUI, digite: 1)')
                        self.stdout.write('')
                        
                        # Aguardar confirmação do usuário
                        response = input('  ❓ Após executar o comando acima, digite "ok" para continuar: ').strip().lower()
                        if response != 'ok':
                            self.stdout.write('  ❌ Configuração cancelada pelo usuário')
                            return False
                        
                        # Verificar se a app foi criada
                        if self._has_tailwind_app():
                            self.stdout.write(f'  ✅ App {self.TAILWIND_APP_NAME} detectada!')
                        else:
                            self.stdout.write(f'  ❌ App {self.TAILWIND_APP_NAME} ainda não foi encontrada')
                            return False
                    
                    # Verificar resultado
                    if process.returncode != 0:
                        self.stdout.write(f'  ❌ Erro ao criar app {self.TAILWIND_APP_NAME}: {stderr}')
                        
                        # Debug apenas em caso de erro
                        self.stdout.write(f'  🔍 Return code: {process.returncode}')
                        self.stdout.write(f'  🔍 STDERR: {repr(stderr)}')
                        
                        # Se o erro indica que o comando tailwind não foi encontrado
                        if 'Unknown command' in stderr or 'tailwind' in stderr:
                            self.stdout.write('')
                            self.stdout.write('  🔧 Isso indica que o django-tailwind não está no INSTALLED_APPS.')
                            self.stdout.write('  💡 Adicione as seguintes apps ao settings.py:')
                            self.stdout.write('')
                            self.stdout.write('  INSTALLED_APPS += [')
                            self.stdout.write("      'tailwind',")
                            self.stdout.write("      'cazenga_ui',")
                            self.stdout.write("      'django_browser_reload',")
                            self.stdout.write("      'mathfilters',")
                            self.stdout.write('  ]')
                            self.stdout.write('')
                            self.stdout.write('  MIDDLEWARE += [')
                            self.stdout.write("      'django_browser_reload.middleware.BrowserReloadMiddleware',")
                            self.stdout.write('  ]')
                            self.stdout.write('')
                            self.stdout.write(f"  TAILWIND_APP_NAME = '{self.TAILWIND_APP_NAME}'")
                            self.stdout.write('  NPM_BIN_PATH = r"C:\\Program Files\\nodejs\\npm.cmd"  # Windows')
                            self.stdout.write('')
                            self.stdout.write('  ✅ Depois de configurar, execute novamente:')
                            self.stdout.write('     python manage.py cazenga init --with-tailwind')
                        
                        return False
                    
                    self.stdout.write(f'  ✅ App {self.TAILWIND_APP_NAME} criada pelo django-tailwind')
                    
                except Exception as inner_e:
                    self.stdout.write(f'  ⚠️ Erro na execução automática: {inner_e}')
                    # Debug em caso de exceção
                    import traceback
                    self.stdout.write(f'  🔍 Traceback: {traceback.format_exc()}')
                    return False
                
            except Exception as e:
                self.stdout.write(f'  ❌ Erro ao configurar django-tailwind: {e}')
                import traceback
                self.stdout.write(f'  🔍 Debug: Traceback completo: {traceback.format_exc()}')
                return False

        return True
    
    def _integrate_with_tailwind(self, theme: str):
        """Integra Django Cazenga UI com estrutura existente do django-tailwind"""
        self.stdout.write('🔗 Integrando com django-tailwind...')
        
        base_dir = Path(settings.BASE_DIR)
        tailwind_app_path = base_dir / self.TAILWIND_APP_NAME
        
        # 1. Substituir styles.css com nosso tema
        self._setup_theme(theme)
        
        # 2. Adicionar components.css
        self._copy_components_css()
        
        # 3. Criar estrutura de componentes
        self._create_components_structure()
        
        # 4. Substituir base.html com nosso template completo
        self._replace_base_template()
        
        # 5. Criar diretórios para assets
        self._create_assets_structure()
        
        # 6. Copiar assets padrão (SPA, etc.)
        self._copy_default_assets()
        
        # 7. Verificar se theme está no INSTALLED_APPS antes dos comandos tailwind
        if not self._verify_theme_in_file():
            self._request_manual_theme_addition()
        
        # 8. Executar comandos tailwind finais
        self._finalize_tailwind_setup()
        
        self.stdout.write('  ✅ Integração concluída')
    
    def _verify_theme_in_file(self):
        """Verifica se theme está realmente no INSTALLED_APPS no settings.py"""
        settings_path = self._get_settings_path()
        if not settings_path:
            return False
        
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Procurar especificamente por theme no INSTALLED_APPS
            pattern = r'INSTALLED_APPS\s*=\s*\[(.*?)\]'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                installed_apps_content = match.group(1)
                return "'theme'" in installed_apps_content or '"theme"' in installed_apps_content
            else:
                return False
        except Exception:
            return False
    
    def _finalize_tailwind_setup(self):
        """Executa comandos finais do tailwind (install + build) com verificação robusta"""
        self.stdout.write('  🔧 Finalizando configuração do Tailwind...')
        
        base_dir = Path(settings.BASE_DIR)
        
        # 1. Executar tailwind install
        self.stdout.write('  📦 Executando tailwind install...')
        success = self._run_tailwind_command('install', base_dir)
        
        # 2. Executar tailwind build
        self.stdout.write('  🏗️ Executando tailwind build...')
        self._run_tailwind_command('build', base_dir)
    
    def _run_tailwind_command(self, command, base_dir):
        """Executa um comando tailwind com tratamento robusto de erros"""
        try:
            process = subprocess.run([
                sys.executable, 'manage.py', 'tailwind', command
            ], cwd=base_dir, capture_output=True, text=True, timeout=60)
            
            if process.returncode == 0:
                self.stdout.write(f'  ✅ tailwind {command} executado com sucesso')
                return True
            else:
                self.stdout.write(f'  ⚠️ Erro no tailwind {command}:')
                if process.stderr:
                    error_lines = process.stderr.strip().split('\n')
                    for line in error_lines:
                        if line.strip():
                            self.stdout.write(f'     {line.strip()}')
                
                # Mostra solução
                self.stdout.write('')
                self.stdout.write('  🔧 Solução:')
                self.stdout.write('     1. Certifique-se de que "theme" está no INSTALLED_APPS em settings.py')
                self.stdout.write('     2. Salve o arquivo settings.py')
                self.stdout.write(f'     3. Execute: python manage.py tailwind {command}')
                
                return False
                
        except subprocess.TimeoutExpired:
            self.stdout.write(f'  ⚠️ Timeout no tailwind {command}')
            self.stdout.write(f'  💡 Execute manualmente: python manage.py tailwind {command}')
            return False
        except Exception as e:
            self.stdout.write(f'  ⚠️ Erro ao executar tailwind {command}: {e}')
            return False
    
    def _setup_theme(self, theme: str):
        """Substitui o styles.css do django-tailwind com nosso tema"""
        self.stdout.write(f'  🎨 Configurando tema "{self.THEMES[theme]["name"]}"...')
        
        base_dir = Path(settings.BASE_DIR)
        source_dir = Path(__file__).parent.parent.parent / 'static_source' / 'css' / 'theme' / theme
        dest_path = base_dir / self.TAILWIND_APP_NAME / 'static_src' / 'src' / 'styles.css'
        source_file = source_dir / 'theme.css'
        
        if not source_file.exists():
            raise CommandError(f'Arquivo de tema não encontrado: {source_file}')
        
        # Substituir styles.css criado pelo django-tailwind
        try:
            shutil.copy2(source_file, dest_path)
            self.stdout.write(f'    ✅ Tema {self.THEMES[theme]["name"]} configurado')
        except Exception as e:
            raise CommandError(f'Erro ao configurar tema: {e}')
    
    def _copy_components_css(self):
        """Adiciona components.css ao static_src/src/"""
        self.stdout.write('  📋 Adicionando components.css...')
        
        base_dir = Path(settings.BASE_DIR)
        source_file = Path(__file__).parent.parent.parent / 'static_source' / 'css' / 'components' / 'components.css'
        dest_path = base_dir / self.TAILWIND_APP_NAME / 'static_src' / 'src' / 'components.css'
        
        if not source_file.exists():
            raise CommandError(f'Arquivo components.css não encontrado: {source_file}')
        
        try:
            shutil.copy2(source_file, dest_path)
            self.stdout.write('    ✅ components.css adicionado')
        except Exception as e:
            raise CommandError(f'Erro ao copiar components.css: {e}')
    
    def _create_components_structure(self):
        """Cria estrutura de diretórios para componentes"""
        self.stdout.write('  📁 Criando estrutura de componentes...')
        
        base_dir = Path(settings.BASE_DIR)
        components_base = base_dir / self.TAILWIND_APP_NAME / 'templates' / 'components'
        
        directories = [
            components_base / 'ui',
            components_base / 'layout',
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.stdout.write('    ✅ Estrutura de componentes criada')
    
    def _create_assets_structure(self):
        """Cria estrutura para assets (JS e ícones)"""
        self.stdout.write('  📦 Criando estrutura de assets...')
        
        base_dir = Path(settings.BASE_DIR)
        static_base = base_dir / self.TAILWIND_APP_NAME / 'static'
        
        directories = [
            static_base / 'js',
            static_base / 'icons',
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.stdout.write('    ✅ Estrutura de assets criada')
    
    def _replace_base_template(self):
        """Substitui completamente o base.html criado pelo django-tailwind"""
        self.stdout.write('  📄 Substituindo template base...')
        
        base_dir = Path(settings.BASE_DIR)
        dest_template_path = base_dir / self.TAILWIND_APP_NAME / 'templates' / 'base.html'
        source_template_path = Path(__file__).parent.parent.parent / 'templates_source' / 'base.html'
        
        if not source_template_path.exists():
            self.stdout.write(f'    ⚠️ Template fonte não encontrado: {source_template_path}')
            return
        
        try:
            # Substitui completamente o base.html
            shutil.copy2(source_template_path, dest_template_path)
            self.stdout.write('    ✅ Template base substituído com versão completa do Cazenga UI')
        except Exception as e:
            self.stdout.write(f'    ⚠️ Erro ao substituir base.html: {e}')
    
    def _copy_default_assets(self):
        """Copia assets padrão (SPA Inteligente, etc.)"""
        self.stdout.write('  📦 Copiando assets padrão...')
        
        base_dir = Path(settings.BASE_DIR)
        js_source_dir = Path(__file__).parent.parent.parent / 'static_source' / 'js'
        js_dest_dir = base_dir / self.TAILWIND_APP_NAME / 'static' / 'js'
        
        # Garante que o diretório de destino existe
        js_dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Assets padrão que são copiados automaticamente
        default_assets = [
            'spa-intelligent.js',  # SPA é padrão
        ]
        
        for asset in default_assets:
            source_file = js_source_dir / asset
            dest_file = js_dest_dir / asset
            
            if source_file.exists():
                try:
                    shutil.copy2(source_file, dest_file)
                    self.stdout.write(f'    ✅ {asset} copiado')
                except Exception as e:
                    self.stdout.write(f'    ⚠️ Erro ao copiar {asset}: {e}')
            else:
                self.stdout.write(f'    ⚠️ Asset não encontrado: {source_file}')
    
    def _enhance_base_template(self):
        """DEPRECATED: Função mantida para compatibilidade, mas substituída por _replace_base_template"""
        # Esta função agora só é chamada se _replace_base_template falhar
        self.stdout.write('  📄 Verificando template base (fallback)...')
        
        base_dir = Path(settings.BASE_DIR)
        base_template_path = base_dir / self.TAILWIND_APP_NAME / 'templates' / 'base.html'
        
        if not base_template_path.exists():
            self.stdout.write('    ⚠️ base.html não encontrado')
            return
        
        # Ler template atual
        try:
            with open(base_template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar se já tem nossas melhorias
            if 'load icon_tags' in content:
                self.stdout.write('    ✅ Template base já está configurado')
                return
            
            # Adicionar load de icon_tags se não existir
            if '{% load static tailwind_tags %}' in content:
                content = content.replace(
                    '{% load static tailwind_tags %}',
                    '{% load static tailwind_tags %}\n{% load icon_tags %}'
                )
                
                with open(base_template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.stdout.write('    ✅ Template base melhorado (icon_tags adicionado)')
            else:
                self.stdout.write('    ⚠️ Template base tem estrutura diferente, não modificado')
        
        except Exception as e:
            self.stdout.write(f'    ⚠️ Erro ao processar base.html: {e}')
    
    def _check_dependencies_status(self):
        """Verifica status das dependências"""
        # Verifica django-tailwind
        try:
            import tailwind
            self.stdout.write('  ✅ django-tailwind instalado')
            
            # Verifica configuração no settings
            if hasattr(settings, 'TAILWIND_APP_NAME'):
                app_name = settings.TAILWIND_APP_NAME
                if app_name == self.TAILWIND_APP_NAME:
                    self.stdout.write(f'  ✅ TAILWIND_APP_NAME configurado: {app_name}')
                else:
                    self.stdout.write(f'  ⚠️ TAILWIND_APP_NAME é "{app_name}", recomendamos "{self.TAILWIND_APP_NAME}"')
            else:
                self.stdout.write('  ❌ TAILWIND_APP_NAME não configurado em settings.py')
        except ImportError:
            self.stdout.write('  ❌ django-tailwind não instalado')
        
        # Verifica outras dependências
        dependencies = [
            ('django-browser-reload', 'django_browser_reload'),
            ('django-mathfilters', 'mathfilters'),
        ]
        
        for dep_name, module_name in dependencies:
            try:
                __import__(module_name)
                self.stdout.write(f'  ✅ {dep_name} instalado')
            except ImportError:
                self.stdout.write(f'  ❌ {dep_name} não instalado')
    
    def _get_current_theme(self) -> Optional[str]:
        """Identifica o tema atual"""
        base_dir = Path(settings.BASE_DIR)
        styles_path = base_dir / self.TAILWIND_APP_NAME / 'static_src' / 'src' / 'styles.css'
        
        if not styles_path.exists():
            return None
        
        try:
            with open(styles_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for theme_key, theme_data in self.THEMES.items():
                if f'Tema {theme_data["name"]}' in content:
                    return theme_data["name"]
            
            return "Não identificado"
        except Exception:
            return None
    
    def _confirm(self, message: str) -> bool:
        """Pede confirmação do usuário"""
        while True:
            response = input(f'{message} [s/N]: ').lower().strip()
            if response in ['s', 'sim', 'y', 'yes']:
                return True
            elif response in ['n', 'não', 'nao', 'no', '']:
                return False
            else:
                print('Por favor, responda com "s" ou "n".')
    
    def _choose_theme(self) -> str:
        """Permite ao usuário escolher um tema"""
        self.stdout.write('\n🎨 Escolha um tema de cores:')
        
        theme_list = list(self.THEMES.items())
        for i, (key, theme) in enumerate(theme_list, 1):
            self.stdout.write(f'  {i}. {theme["name"]:<10} - {theme["description"]}')
        
        while True:
            try:
                choice = input(f'\nEscolha um tema (1-{len(theme_list)}) [1]: ').strip()
                
                if not choice:
                    choice = '1'
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(theme_list):
                    selected_theme = theme_list[choice_num - 1][0]
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Tema selecionado: {self.THEMES[selected_theme]["name"]}')
                    )
                    return selected_theme
                else:
                    print(f'Por favor, escolha um número entre 1 e {len(theme_list)}.')
            except ValueError:
                print('Por favor, digite um número válido.')
    
    def _show_success_message(self, theme: str, with_tailwind: bool):
        """Mostra mensagem de sucesso ATUALIZADA"""
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Django Cazenga UI configurado com sucesso!')
        )
        
        self.stdout.write(f'   🎨 Tema: {self.THEMES[theme]["name"]}')
        self.stdout.write(f'   🛠️ Django-tailwind: {"Configurado automaticamente" if with_tailwind else "Já configurado"}')
        self.stdout.write('   📦 Dependências npm: Instaladas automaticamente')
        self.stdout.write('   🏗️ CSS compilado: Build executado automaticamente')
        
        self.stdout.write('\n🚀 Pronto para usar! Execute:')
        self.stdout.write('   python manage.py runserver')
        
        self.stdout.write('\n🔧 Comandos adicionais:')
        self.stdout.write('   python manage.py tailwind start     # Modo desenvolvimento (watch)')
        self.stdout.write('   python manage.py ui add button      # Adicionar componentes')
        self.stdout.write('   python manage.py ui icons --install # Instalar ícones')
        
        self.stdout.write('\n📖 Documentação:')
        self.stdout.write('   python manage.py ui list            # Lista componentes')
        self.stdout.write('   python manage.py cazenga themes     # Lista temas')
        self.stdout.write('   python manage.py cazenga status     # Status detalhado')
        
        self.stdout.write(f'\n✨ Tudo configurado automaticamente!')
        
        self.stdout.write('\n📝 Estrutura criada:')
        self.stdout.write(f'  📁 {self.TAILWIND_APP_NAME}/templates/components/ui/     (componentes UI)')
        self.stdout.write(f'  📁 {self.TAILWIND_APP_NAME}/templates/components/layout/ (componentes Layout)')
        self.stdout.write(f'  📁 {self.TAILWIND_APP_NAME}/static/js/                   (arquivos JavaScript)')
        self.stdout.write(f'  📁 {self.TAILWIND_APP_NAME}/static/icons/                (ícones SVG)')
        self.stdout.write(f'  📁 {self.TAILWIND_APP_NAME}/static_src/src/              (CSS fonte - temas)')
        
        self.stdout.write('\n🎯 Arquitetura:')
        self.stdout.write('  📦 cazenga_ui (biblioteca) - comandos e funcionalidades')
        self.stdout.write(f'  📁 {self.TAILWIND_APP_NAME} (app local) - templates e assets estáticos')
    
    def print_help(self):
        """Mostra ajuda do comando"""
        self.stdout.write(
            self.style.SUCCESS('\n🎨 Django Cazenga UI - Comando Principal\n')
        )
        
        self.stdout.write('Uso: python manage.py cazenga <ação> [opções]\n')
        
        self.stdout.write('Ações disponíveis:')
        self.stdout.write('  init                    Integra com django-tailwind existente')
        self.stdout.write('  init --with-tailwind    Configura django-tailwind + integra')
        self.stdout.write('  init --theme <tema>     Especifica tema (senão pergunta)')
        self.stdout.write('  themes                  Lista temas disponíveis')
        self.stdout.write('  switch-theme <tema>     Altera tema do projeto')
        self.stdout.write('  status                  Mostra status da configuração')
        
        self.stdout.write('\nExemplos:')
        self.stdout.write('  python manage.py cazenga init --with-tailwind --theme roxo')
        self.stdout.write('  python manage.py cazenga init  # Se django-tailwind já configurado')
        self.stdout.write('  python manage.py cazenga themes')
        self.stdout.write('  python manage.py cazenga switch-theme verde')
        self.stdout.write('  python manage.py cazenga status')
        
        self.stdout.write('\n💡 Instalação recomendada:')
        self.stdout.write('  pip install django-cazenga-ui')
        self.stdout.write('  python manage.py cazenga init --with-tailwind --theme roxo')
    
    def _request_manual_theme_addition(self):
        """Solicita ao usuário que adicione manualmente 'theme' ao INSTALLED_APPS"""
        self.stdout.write('\n⏸️  AÇÃO NECESSÁRIA:')
        self.stdout.write('')
        self.stdout.write('  📋 Você precisa adicionar a app "theme" ao INSTALLED_APPS em settings.py')
        self.stdout.write('')
        
        # Mostrar localização do settings.py
        settings_path = self._get_settings_path()
        if settings_path:
            self.stdout.write(f'  📁 Arquivo: {settings_path}')
        
        self.stdout.write('')
        self.stdout.write('  🔧 Adicione esta linha ao INSTALLED_APPS:')
        self.stdout.write("      'theme',")
        self.stdout.write('')
        self.stdout.write('  💡 Exemplo completo:')
        self.stdout.write('      INSTALLED_APPS = [')
        self.stdout.write('          ...')
        self.stdout.write("          'tailwind',")
        self.stdout.write("          'cazenga_ui',")
        self.stdout.write("          'django_browser_reload',")
        self.stdout.write("          'mathfilters',")
        self.stdout.write("          'theme',  # ← Adicione esta linha")
        self.stdout.write('      ]')
        self.stdout.write('')
        
        # Aguardar confirmação do usuário
        while True:
            try:
                response = input('🔄 Após adicionar "theme" ao INSTALLED_APPS, digite 1 para continuar: ').strip()
                if response == '1':
                    break
                else:
                    self.stdout.write('  ❌ Digite apenas "1" para continuar')
            except KeyboardInterrupt:
                self.stdout.write('\n❌ Operação cancelada pelo usuário')
                return
            except Exception:
                self.stdout.write('  ❌ Entrada inválida. Digite apenas "1" para continuar')
        
        # Verificar se foi adicionado
        if self._verify_theme_in_file():
            self.stdout.write('  ✅ "theme" encontrado no INSTALLED_APPS!')
            self.stdout.write('  🔄 Continuando com a instalação...')
        else:
            self.stdout.write('  ⚠️ "theme" ainda não foi encontrado no INSTALLED_APPS')
            self.stdout.write('  💡 Certifique-se de salvar o arquivo settings.py')
            self.stdout.write('  🔄 Continuando mesmo assim...')
    
    def _get_settings_path(self) -> Optional[Path]:
        """Encontra o caminho do settings.py"""
        base_dir = Path(settings.BASE_DIR)
        
        # Procura por settings.py na estrutura do projeto
        possible_paths = [
            base_dir / 'settings.py',
            base_dir / f'{base_dir.name}' / 'settings.py',
        ]
        
        # Verifica via DJANGO_SETTINGS_MODULE
        settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', '')
        if settings_module:
            module_path = settings_module.replace('.', '/') + '.py'
            possible_paths.append(base_dir / module_path)
        
        for path in possible_paths:
            if path.exists():
                return path
        
        # Fallback: busca recursivamente
        for settings_file in base_dir.rglob('settings.py'):
            if 'venv' not in str(settings_file) and 'site-packages' not in str(settings_file):
                return settings_file
        
        return None 