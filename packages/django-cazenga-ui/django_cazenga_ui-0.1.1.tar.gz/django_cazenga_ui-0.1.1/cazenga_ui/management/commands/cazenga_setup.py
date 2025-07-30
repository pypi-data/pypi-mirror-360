"""
Comando de diagnóstico e configuração para Django Cazenga UI
Este comando funciona mesmo sem configurações no settings.py
"""

import os
import re
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    """Comando de diagnóstico e configuração inicial"""
    
    help = 'Diagnóstico e orientações para configurar Django Cazenga UI'
    
    def add_arguments(self, parser):
        """Adiciona argumentos ao comando"""
        parser.add_argument(
            '--auto-configure',
            action='store_true',
            help='Configura automaticamente o settings.py (com confirmação)'
        )
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Confirma automaticamente todas as alterações'
        )
    
    def handle(self, *args, **options):
        """Executa diagnóstico e fornece orientações"""
        self.stdout.write(
            self.style.SUCCESS('\n🔍 Diagnóstico Django Cazenga UI\n')
        )
        
        # Verifica se as dependências estão instaladas
        dependencies = self._check_dependencies()
        
        # Verifica configuração do settings.py
        config_status = self._check_settings_config()
        
        # Mostra status
        self._show_status(dependencies, config_status)
        
        # Auto-configuração se solicitada
        if options['auto_configure'] or options['yes']:
            self._auto_configure(config_status, options['yes'])
        else:
            # Mostra orientações
            self._show_instructions(dependencies, config_status)
    
    def _auto_configure(self, config_status: dict, auto_yes: bool = False):
        """Configura automaticamente o settings.py"""
        self.stdout.write('\n🔧 Auto-configuração do settings.py\n')
        
        # Identifica o que precisa ser adicionado
        missing_items = []
        
        if not config_status['cazenga_ui']:
            missing_items.append("'cazenga_ui' no INSTALLED_APPS")
        if not config_status['tailwind']:
            missing_items.append("'tailwind' no INSTALLED_APPS")
        if not config_status['django_browser_reload']:
            missing_items.append("'django_browser_reload' no INSTALLED_APPS")
        if not config_status['mathfilters']:
            missing_items.append("'mathfilters' no INSTALLED_APPS")
        if not config_status['browser_reload_middleware']:
            missing_items.append("BrowserReloadMiddleware no MIDDLEWARE")
        if not config_status['tailwind_app_name']:
            missing_items.append("TAILWIND_APP_NAME = 'theme'")
        if not config_status['npm_bin_path']:
            missing_items.append("NPM_BIN_PATH")
        
        if not missing_items:
            self.stdout.write('✅ Todas as configurações já estão presentes!')
            return
        
        # Mostra o que será adicionado
        self.stdout.write('📋 Itens que serão adicionados:')
        for item in missing_items:
            self.stdout.write(f'  + {item}')
        
        # Confirmação
        if not auto_yes:
            confirm = input('\n❓ Deseja continuar com a auto-configuração? [s/N]: ').lower().strip()
            if confirm not in ['s', 'sim', 'y', 'yes']:
                self.stdout.write('❌ Auto-configuração cancelada.')
                self._show_instructions({}, config_status)
                return
        
        # Faz backup
        settings_path = self._get_settings_path()
        if not self._backup_settings(settings_path):
            return
        
        # Aplica as configurações
        success = self._apply_configurations(settings_path, config_status)
        
        if success:
            self.stdout.write('\n✅ Auto-configuração concluída com sucesso!')
            self.stdout.write('💾 Backup salvo como: settings.py.backup')
            self.stdout.write('\n🎯 Próximo passo:')
            self.stdout.write('   python manage.py cazenga init --with-tailwind')
        else:
            self.stdout.write('\n❌ Erro na auto-configuração.')
            self.stdout.write('💾 Arquivo original restaurado do backup.')
    
    def _get_settings_path(self) -> Path:
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
        
        raise FileNotFoundError('Arquivo settings.py não encontrado')
    
    def _backup_settings(self, settings_path: Path) -> bool:
        """Faz backup do settings.py"""
        backup_path = settings_path.with_suffix('.py.backup')
        
        try:
            shutil.copy2(settings_path, backup_path)
            self.stdout.write(f'💾 Backup criado: {backup_path}')
            return True
        except Exception as e:
            self.stdout.write(f'❌ Erro ao criar backup: {e}')
            return False
    
    def _apply_configurations(self, settings_path: Path, config_status: dict) -> bool:
        """Aplica as configurações no settings.py"""
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Adiciona apps ao INSTALLED_APPS
            content = self._add_installed_apps(content, config_status)
            
            # Adiciona middleware
            content = self._add_middleware(content, config_status)
            
            # Adiciona configurações no final
            content = self._add_settings(content, config_status)
            
            # Salva o arquivo modificado
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            self.stdout.write(f'❌ Erro ao modificar settings.py: {e}')
            # Restaura backup
            backup_path = settings_path.with_suffix('.py.backup')
            if backup_path.exists():
                shutil.copy2(backup_path, settings_path)
            return False
    
    def _add_installed_apps(self, content: str, config_status: dict) -> str:
        """Adiciona apps ao INSTALLED_APPS"""
        apps_to_add = []
        
        if not config_status['tailwind']:
            apps_to_add.append("    'tailwind',")
        if not config_status['cazenga_ui']:
            apps_to_add.append("    'cazenga_ui',")
        if not config_status['django_browser_reload']:
            apps_to_add.append("    'django_browser_reload',")
        if not config_status['mathfilters']:
            apps_to_add.append("    'mathfilters',")
        
        if not apps_to_add:
            return content
        
        # Procura INSTALLED_APPS
        pattern = r'(INSTALLED_APPS\s*=\s*\[)(.*?)(\])'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            # Adiciona as apps antes do ]
            apps_section = match.group(2)
            # Remove trailing whitespace and comma if needed
            apps_section = apps_section.rstrip()
            if not apps_section.endswith(','):
                apps_section += ','
            
            new_apps = '\n' + '\n'.join(apps_to_add)
            new_installed_apps = f"{match.group(1)}{apps_section}{new_apps}\n{match.group(3)}"
            
            content = content.replace(match.group(0), new_installed_apps)
            self.stdout.write('✅ Apps adicionadas ao INSTALLED_APPS')
        
        return content
    
    def _add_middleware(self, content: str, config_status: dict) -> str:
        """Adiciona middleware ao MIDDLEWARE"""
        if config_status['browser_reload_middleware']:
            return content
        
        middleware_line = "    'django_browser_reload.middleware.BrowserReloadMiddleware',"
        
        # Procura MIDDLEWARE
        pattern = r'(MIDDLEWARE\s*=\s*\[)(.*?)(\])'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            # Adiciona o middleware antes do ]
            middleware_section = match.group(2)
            middleware_section = middleware_section.rstrip()
            if not middleware_section.endswith(','):
                middleware_section += ','
            
            new_middleware = f"{match.group(1)}{middleware_section}\n{middleware_line}\n{match.group(3)}"
            content = content.replace(match.group(0), new_middleware)
            self.stdout.write('✅ BrowserReloadMiddleware adicionado ao MIDDLEWARE')
        
        return content
    
    def _add_settings(self, content: str, config_status: dict) -> str:
        """Adiciona configurações no final do arquivo"""
        settings_to_add = []
        
        if not config_status['tailwind_app_name']:
            settings_to_add.append("TAILWIND_APP_NAME = 'theme'")
        
        if not config_status['npm_bin_path']:
            settings_to_add.append('NPM_BIN_PATH = r"C:\\Program Files\\nodejs\\npm.cmd"  # Windows')
        
        if settings_to_add:
            # Adiciona as configurações no final
            django_cazenga_config = [
                '',
                '# Django Cazenga UI Configuration',
            ] + settings_to_add
            
            content += '\n' + '\n'.join(django_cazenga_config) + '\n'
            self.stdout.write('✅ Configurações Django Cazenga UI adicionadas')
        
        return content
    
    def _check_dependencies(self) -> dict:
        """Verifica se as dependências estão instaladas via pip"""
        deps = {}
        
        try:
            import tailwind
            deps['django-tailwind'] = True
        except ImportError:
            deps['django-tailwind'] = False
        
        try:
            import django_browser_reload
            deps['django-browser-reload'] = True
        except ImportError:
            deps['django-browser-reload'] = False
        
        try:
            import mathfilters
            deps['django-mathfilters'] = True
        except ImportError:
            deps['django-mathfilters'] = False
        
        # cazenga_ui sempre estará disponível se este comando executar
        deps['django-cazenga-ui'] = True
        
        return deps
    
    def _check_settings_config(self) -> dict:
        """Verifica configuração no settings.py"""
        config = {}
        
        installed_apps = getattr(settings, 'INSTALLED_APPS', [])
        
        config['cazenga_ui'] = 'cazenga_ui' in installed_apps
        config['tailwind'] = 'tailwind' in installed_apps
        config['django_browser_reload'] = 'django_browser_reload' in installed_apps
        config['mathfilters'] = 'mathfilters' in installed_apps
        config['theme'] = 'theme' in installed_apps  # App criada pelo django-tailwind
        
        config['tailwind_app_name'] = hasattr(settings, 'TAILWIND_APP_NAME')
        config['npm_bin_path'] = hasattr(settings, 'NPM_BIN_PATH')
        
        middleware = getattr(settings, 'MIDDLEWARE', [])
        config['browser_reload_middleware'] = 'django_browser_reload.middleware.BrowserReloadMiddleware' in middleware
        
        return config
    
    def _show_status(self, dependencies: dict, config: dict):
        """Mostra status atual"""
        self.stdout.write('📦 Dependências instaladas:')
        for dep, installed in dependencies.items():
            status = "✅" if installed else "❌"
            self.stdout.write(f'  {status} {dep}')
        
        self.stdout.write('\n⚙️ Configuração settings.py:')
        for setting, configured in config.items():
            status = "✅" if configured else "❌"
            setting_name = setting.replace('_', '-').title()
            self.stdout.write(f'  {status} {setting_name}')
    
    def _show_instructions(self, dependencies: dict, config: dict):
        """Mostra instruções baseadas no status"""
        self.stdout.write('\n📋 Instruções:')
        
        # Se dependências não estão instaladas
        missing_deps = [dep for dep, installed in dependencies.items() if not installed]
        if missing_deps:
            self.stdout.write('\n1️⃣ Instale as dependências:')
            self.stdout.write('   pip install django-cazenga-ui')
            self.stdout.write('')
        
        # Se configuração está incompleta
        missing_config = [conf for conf, configured in config.items() if not configured and conf != 'theme']
        if missing_config:
            self.stdout.write('2️⃣ Configure o settings.py:')
            self.stdout.write('')
            self.stdout.write('   INSTALLED_APPS += [')
            if not config['tailwind']:
                self.stdout.write("       'tailwind',")
            if not config['cazenga_ui']:
                self.stdout.write("       'cazenga_ui',")
            if not config['django_browser_reload']:
                self.stdout.write("       'django_browser_reload',")
            if not config['mathfilters']:
                self.stdout.write("       'mathfilters',")
            self.stdout.write('   ]')
            self.stdout.write('')
            
            if not config['browser_reload_middleware']:
                self.stdout.write('   MIDDLEWARE += [')
                self.stdout.write("       'django_browser_reload.middleware.BrowserReloadMiddleware',")
                self.stdout.write('   ]')
                self.stdout.write('')
            
            if not config['tailwind_app_name']:
                self.stdout.write("   TAILWIND_APP_NAME = 'theme'")
            if not config['npm_bin_path']:
                self.stdout.write('   NPM_BIN_PATH = r"C:\\Program Files\\nodejs\\npm.cmd"  # Windows')
            
            self.stdout.write('')
            self.stdout.write('   💡 Ou use a auto-configuração:')
            self.stdout.write('      python manage.py cazenga-setup --auto-configure')
            self.stdout.write('')
        
        # Se tudo configurado
        all_deps_ok = all(dependencies.values())
        main_config_ok = all(config[k] for k in config if k != 'theme')  # Excluir 'theme' da verificação inicial
        
        if all_deps_ok and main_config_ok:
            self.stdout.write('✅ Configuração completa!')
            self.stdout.write('\n3️⃣ Execute o comando principal:')
            self.stdout.write('   python manage.py cazenga init --with-tailwind')
        else:
            self.stdout.write('3️⃣ Após configurar, execute:')
            self.stdout.write('   python manage.py cazenga init --with-tailwind')
        
        self.stdout.write('\n💡 Comandos disponíveis:')
        self.stdout.write('   python manage.py cazenga-setup                # Este diagnóstico')
        self.stdout.write('   python manage.py cazenga-setup --auto-configure  # Auto-configuração')
        if config['cazenga_ui']:
            self.stdout.write('   python manage.py cazenga init               # Configuração principal')
            self.stdout.write('   python manage.py cazenga themes             # Lista temas')
            self.stdout.write('   python manage.py cazenga status             # Status detalhado')
        else:
            self.stdout.write('   python manage.py cazenga [...]              # Disponível após configurar') 