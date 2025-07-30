#!/usr/bin/env python3
"""
Django Cazenga UI - CLI Independente
Comando que funciona sem precisar do Django configurado
"""

import os
import re
import sys
import shutil
import argparse
from pathlib import Path


def find_settings_file(base_dir=None):
    """Encontra o arquivo settings.py do projeto Django"""
    if base_dir is None:
        base_dir = Path.cwd()
    else:
        base_dir = Path(base_dir)
    
    # Procura por manage.py primeiro (indica projeto Django)
    manage_py = base_dir / 'manage.py'
    if not manage_py.exists():
        print("❌ Não encontrado manage.py - certifique-se de estar no diretório do projeto Django")
        return None
    
    # Procura por settings.py
    possible_paths = [
        base_dir / 'settings.py',
        base_dir / f'{base_dir.name}' / 'settings.py',
    ]
    
    # Busca recursivamente
    for settings_file in base_dir.rglob('settings.py'):
        if 'venv' not in str(settings_file) and 'site-packages' not in str(settings_file):
            possible_paths.append(settings_file)
    
    for path in possible_paths:
        if path.exists():
            return path
    
    print("❌ Arquivo settings.py não encontrado")
    return None


def find_main_urls_file(base_dir=None):
    """Encontra o arquivo urls.py principal do projeto Django"""
    if base_dir is None:
        base_dir = Path.cwd()
    else:
        base_dir = Path(base_dir)
    
    # Procura por urls.py na estrutura do projeto
    possible_paths = [
        base_dir / 'urls.py',
        base_dir / f'{base_dir.name}' / 'urls.py',
    ]
    
    # Busca recursivamente, mas prioriza o que tem 'admin' (geralmente é o principal)
    for urls_file in base_dir.rglob('urls.py'):
        if 'venv' not in str(urls_file) and 'site-packages' not in str(urls_file):
            try:
                with open(urls_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Se contém 'admin', provavelmente é o urls.py principal
                    if 'admin.site.urls' in content:
                        return urls_file
            except:
                continue
    
    # Fallback para primeira encontrada
    for path in possible_paths:
        if path.exists():
            return path
    
    return None


def check_dependencies():
    """Verifica se as dependências estão instaladas"""
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
    
    try:
        import cazenga_ui
        deps['django-cazenga-ui'] = True
    except ImportError:
        deps['django-cazenga-ui'] = False
    
    return deps


def check_settings_config(settings_path):
    """Verifica configuração no settings.py"""
    if not settings_path.exists():
        return {}
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Erro ao ler settings.py: {e}")
        return {}
    
    config = {}
    
    # Verifica INSTALLED_APPS
    config['cazenga_ui'] = "'cazenga_ui'" in content or '"cazenga_ui"' in content
    config['tailwind'] = "'tailwind'" in content or '"tailwind"' in content
    config['django_browser_reload'] = "'django_browser_reload'" in content or '"django_browser_reload"' in content
    config['mathfilters'] = "'mathfilters'" in content or '"mathfilters"' in content
    config['theme'] = "'theme'" in content or '"theme"' in content
    
    # Verifica configurações
    config['tailwind_app_name'] = 'TAILWIND_APP_NAME' in content
    config['npm_bin_path'] = 'NPM_BIN_PATH' in content
    
    # Verifica middleware
    config['browser_reload_middleware'] = 'django_browser_reload.middleware.BrowserReloadMiddleware' in content
    
    return config


def check_urls_config(urls_path):
    """Verifica configuração no urls.py principal"""
    if not urls_path or not urls_path.exists():
        return {}
    
    try:
        with open(urls_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Erro ao ler urls.py: {e}")
        return {}
    
    config = {}
    
    # Verifica imports necessários
    config['has_include_import'] = 'from django.urls import include' in content or 'from django.urls import path, include' in content
    
    # Verifica URL do browser reload
    config['browser_reload_url'] = '__reload__' in content and 'django_browser_reload.urls' in content
    
    return config


def backup_settings(settings_path):
    """Faz backup do settings.py"""
    backup_path = settings_path.with_suffix('.py.backup')
    
    try:
        shutil.copy2(settings_path, backup_path)
        print(f"💾 Backup criado: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return False


def backup_urls(urls_path):
    """Faz backup do urls.py"""
    backup_path = urls_path.with_suffix('.py.backup')
    
    try:
        shutil.copy2(urls_path, backup_path)
        print(f"💾 Backup do urls.py criado: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar backup do urls.py: {e}")
        return False


def add_installed_apps(content, config_status):
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
    # NOTA: 'theme' não é adicionado aqui porque a app só é criada pelo comando 'cazenga init'
    
    if not apps_to_add:
        return content
    
    # Procura INSTALLED_APPS
    pattern = r'(INSTALLED_APPS\s*=\s*\[)(.*?)(\])'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # Adiciona as apps antes do ]
        apps_section = match.group(2)
        apps_section = apps_section.rstrip()
        if not apps_section.endswith(','):
            apps_section += ','
        
        new_apps = '\n' + '\n'.join(apps_to_add)
        new_installed_apps = f"{match.group(1)}{apps_section}{new_apps}\n{match.group(3)}"
        
        content = content.replace(match.group(0), new_installed_apps)
        print('✅ Apps adicionadas ao INSTALLED_APPS')
    
    return content


def add_middleware(content, config_status):
    """Adiciona middleware ao MIDDLEWARE"""
    if config_status['browser_reload_middleware']:
        return content
    
    middleware_line = "    'django_browser_reload.middleware.BrowserReloadMiddleware',"
    
    # Procura MIDDLEWARE
    pattern = r'(MIDDLEWARE\s*=\s*\[)(.*?)(\])'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        middleware_section = match.group(2)
        middleware_section = middleware_section.rstrip()
        if not middleware_section.endswith(','):
            middleware_section += ','
        
        new_middleware = f"{match.group(1)}{middleware_section}\n{middleware_line}\n{match.group(3)}"
        content = content.replace(match.group(0), new_middleware)
        print('✅ BrowserReloadMiddleware adicionado ao MIDDLEWARE')
    
    return content


def add_settings(content, config_status):
    """Adiciona configurações no final do arquivo"""
    settings_to_add = []
    
    if not config_status['tailwind_app_name']:
        settings_to_add.append("TAILWIND_APP_NAME = 'theme'")
    
    if not config_status['npm_bin_path']:
        settings_to_add.append('NPM_BIN_PATH = r"C:\\Program Files\\nodejs\\npm.cmd"  # Windows')
    
    if settings_to_add:
        django_cazenga_config = [
            '',
            '# Django Cazenga UI Configuration',
        ] + settings_to_add
        
        content += '\n' + '\n'.join(django_cazenga_config) + '\n'
        print('✅ Configurações Django Cazenga UI adicionadas')
    
    return content


def add_browser_reload_url(content, urls_config):
    """Adiciona URL do django-browser-reload ao urls.py"""
    
    # Primeiro, garantir que tem o import include
    if not urls_config['has_include_import']:
        # Verifica se já tem algum import de django.urls
        if 'from django.urls import path' in content:
            content = content.replace(
                'from django.urls import path',
                'from django.urls import path, include'
            )
            print('✅ Import include adicionado')
        else:
            # Adiciona import completo
            import_line = 'from django.urls import path, include\n'
            # Encontra onde inserir (após outros imports)
            lines = content.split('\n')
            insert_index = 0
            for i, line in enumerate(lines):
                if line.startswith('from django.') or line.startswith('import '):
                    insert_index = i + 1
            lines.insert(insert_index, import_line.strip())
            content = '\n'.join(lines)
            print('✅ Import django.urls adicionado')
    
    # Adicionar URL do browser reload se não existir
    if not urls_config['browser_reload_url']:
        reload_url = '    path("__reload__/", include("django_browser_reload.urls")),'
        
        # Procura urlpatterns
        pattern = r'(urlpatterns\s*=\s*\[)(.*?)(\])'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            urls_section = match.group(2)
            urls_section = urls_section.rstrip()
            if not urls_section.endswith(','):
                urls_section += ','
            
            new_urlpatterns = f"{match.group(1)}{urls_section}\n{reload_url}\n{match.group(3)}"
            content = content.replace(match.group(0), new_urlpatterns)
            print('✅ URL __reload__/ adicionada ao urlpatterns')
    
    return content


def auto_configure(settings_path, urls_path, config_status, urls_config, auto_yes=False):
    """Configura automaticamente o settings.py e urls.py"""
    print('\n🔧 Auto-configuração do Django\n')
    
    # Identifica o que precisa ser adicionado
    missing_items = []
    
    # Settings.py
    if not config_status['cazenga_ui']:
        missing_items.append("'cazenga_ui' no INSTALLED_APPS")
    if not config_status['tailwind']:
        missing_items.append("'tailwind' no INSTALLED_APPS")
    if not config_status['django_browser_reload']:
        missing_items.append("'django_browser_reload' no INSTALLED_APPS")
    if not config_status['mathfilters']:
        missing_items.append("'mathfilters' no INSTALLED_APPS")
    # NOTA: 'theme' não é verificado aqui porque será adicionado pelo comando 'cazenga init'
    if not config_status['browser_reload_middleware']:
        missing_items.append("BrowserReloadMiddleware no MIDDLEWARE")
    if not config_status['tailwind_app_name']:
        missing_items.append("TAILWIND_APP_NAME = 'theme'")
    if not config_status['npm_bin_path']:
        missing_items.append("NPM_BIN_PATH")
    
    # URLs.py
    if urls_path and not urls_config['has_include_import']:
        missing_items.append("Import 'include' no urls.py")
    if urls_path and not urls_config['browser_reload_url']:
        missing_items.append("URL '__reload__/' no urls.py")
    
    if not missing_items:
        print('✅ Todas as configurações já estão presentes!')
        return True
    
    # Mostra o que será adicionado
    print('📋 Itens que serão adicionados:')
    for item in missing_items:
        print(f'  + {item}')
    
    # Confirmação
    if not auto_yes:
        confirm = input('\n❓ Deseja continuar com a auto-configuração? [s/N]: ').lower().strip()
        if confirm not in ['s', 'sim', 'y', 'yes']:
            print('❌ Auto-configuração cancelada.')
            return False
    
    # Fazer backups
    if not backup_settings(settings_path):
        return False
    
    if urls_path and (not urls_config['has_include_import'] or not urls_config['browser_reload_url']):
        if not backup_urls(urls_path):
            return False
    
    # Configurar settings.py
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings_content = f.read()
        
        settings_content = add_installed_apps(settings_content, config_status)
        settings_content = add_middleware(settings_content, config_status)
        settings_content = add_settings(settings_content, config_status)
        
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(settings_content)
        
        print('✅ Settings.py configurado')
        
    except Exception as e:
        print(f'❌ Erro ao modificar settings.py: {e}')
        return False
    
    # Configurar urls.py
    if urls_path and (not urls_config['has_include_import'] or not urls_config['browser_reload_url']):
        try:
            with open(urls_path, 'r', encoding='utf-8') as f:
                urls_content = f.read()
            
            urls_content = add_browser_reload_url(urls_content, urls_config)
            
            with open(urls_path, 'w', encoding='utf-8') as f:
                f.write(urls_content)
            
            print('✅ URLs.py configurado')
            
        except Exception as e:
            print(f'❌ Erro ao modificar urls.py: {e}')
            return False
    
    print('\n✅ Auto-configuração concluída com sucesso!')
    print('💾 Backups salvos como .backup')
    print('\n🎯 Próximo passo:')
    print('   python manage.py cazenga init --with-tailwind')
    print('   (Este comando irá criar a app \'theme\' e adicioná-la ao INSTALLED_APPS)')
    return True


def show_status(dependencies, config, urls_config, urls_path):
    """Mostra status atual"""
    print('📦 Dependências instaladas:')
    for dep, installed in dependencies.items():
        status = "✅" if installed else "❌"
        print(f'  {status} {dep}')
    
    print('\n⚙️ Configuração settings.py:')
    for setting, configured in config.items():
        status = "✅" if configured else "❌"
        setting_name = setting.replace('_', '-').title()
        print(f'  {status} {setting_name}')
    
    print('\n🔗 Configuração urls.py:')
    if urls_path:
        for setting, configured in urls_config.items():
            status = "✅" if configured else "❌"
            if setting == 'has_include_import':
                print(f'  {status} Import include')
            elif setting == 'browser_reload_url':
                print(f'  {status} URL __reload__/')
    else:
        print('  ❌ URLs.py principal não encontrado')


def show_instructions(dependencies, config, urls_config, urls_path):
    """Mostra instruções baseadas no status"""
    print('\n📋 Instruções:')
    
    # Se dependências não estão instaladas
    missing_deps = [dep for dep, installed in dependencies.items() if not installed]
    if missing_deps:
        print('\n1️⃣ Instale as dependências:')
        print('   pip install django-cazenga-ui')
        print('')
    
    # Se configuração está incompleta
    missing_config = [conf for conf, configured in config.items() if not configured]
    missing_urls = [conf for conf, configured in urls_config.items() if not configured] if urls_path else []
    
    if missing_config or missing_urls:
        print('2️⃣ Configure automaticamente:')
        print('   cazenga-setup --auto-configure')
        print('')
        print('   Ou configure manualmente:')
        print('')
        
        if missing_config:
            print('   📄 settings.py:')
            print('   INSTALLED_APPS += [')
            if not config['tailwind']:
                print("       'tailwind',")
            if not config['cazenga_ui']:
                print("       'cazenga_ui',")
            if not config['django_browser_reload']:
                print("       'django_browser_reload',")
            if not config['mathfilters']:
                print("       'mathfilters',")
            # NOTA: 'theme' será adicionado automaticamente pelo comando 'cazenga init'
            print('   ]')
            print('')
            
            if not config['browser_reload_middleware']:
                print('   MIDDLEWARE += [')
                print("       'django_browser_reload.middleware.BrowserReloadMiddleware',")
                print('   ]')
                print('')
            
            if not config['tailwind_app_name']:
                print("   TAILWIND_APP_NAME = 'theme'")
            if not config['npm_bin_path']:
                print('   NPM_BIN_PATH = r"C:\\Program Files\\nodejs\\npm.cmd"  # Windows')
            print('')
        
        if missing_urls and urls_path:
            print('   📄 urls.py:')
            if not urls_config['has_include_import']:
                print('   from django.urls import path, include')
            print('   urlpatterns += [')
            if not urls_config['browser_reload_url']:
                print('       path("__reload__/", include("django_browser_reload.urls")),')
            print('   ]')
            print('')
    
    # Se tudo configurado
    all_deps_ok = all(dependencies.values())
    # Verifica config exceto 'theme' (que será adicionado pelo comando 'cazenga init')
    main_config_ok = all(config[k] for k in config if k != 'theme')
    urls_config_ok = all(urls_config.values()) if urls_path else True
    
    if all_deps_ok and main_config_ok and urls_config_ok:
        print('✅ Configuração completa!')
        print('\n3️⃣ Execute o comando principal:')
        print('   python manage.py cazenga init --with-tailwind')
        print('   (Este comando irá criar a app \'theme\' e adicioná-la ao INSTALLED_APPS)')
    else:
        print('3️⃣ Após configurar, execute:')
        print('   python manage.py cazenga init --with-tailwind')
        print('   (Este comando irá criar a app \'theme\' e adicioná-la ao INSTALLED_APPS)')


def main():
    """Função principal do CLI"""
    parser = argparse.ArgumentParser(
        description='Django Cazenga UI - Configuração Automática',
        prog='cazenga-setup'
    )
    
    parser.add_argument(
        '--auto-configure',
        action='store_true',
        help='Configura automaticamente o settings.py e urls.py (com confirmação)'
    )
    parser.add_argument(
        '--yes',
        action='store_true',
        help='Confirma automaticamente todas as alterações'
    )
    parser.add_argument(
        '--dir',
        help='Diretório do projeto Django (padrão: diretório atual)'
    )
    
    args = parser.parse_args()
    
    print('🔍 Django Cazenga UI - Configuração Automática\n')
    
    # Encontra os arquivos do projeto
    settings_path = find_settings_file(args.dir)
    if not settings_path:
        sys.exit(1)
    
    urls_path = find_main_urls_file(args.dir)
    
    print(f'📁 Projeto encontrado: {settings_path.parent}')
    print(f'⚙️  Settings: {settings_path}')
    if urls_path:
        print(f'🔗 URLs: {urls_path}')
    else:
        print('🔗 URLs: ❌ não encontrado')
    
    # Verifica dependências
    dependencies = check_dependencies()
    
    # Verifica configuração
    config_status = check_settings_config(settings_path)
    urls_config = check_urls_config(urls_path) if urls_path else {}
    
    # Mostra status
    show_status(dependencies, config_status, urls_config, urls_path)
    
    # Auto-configuração se solicitada
    if args.auto_configure or args.yes:
        success = auto_configure(settings_path, urls_path, config_status, urls_config, args.yes)
        if not success:
            sys.exit(1)
    else:
        # Mostra instruções
        show_instructions(dependencies, config_status, urls_config, urls_path)


if __name__ == '__main__':
    main() 