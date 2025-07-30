"""
Comando UI para Django Cazenga UI
Gerencia componentes de interface do usuário
"""

import os
import shutil
from pathlib import Path
from typing import List, Set

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from cazenga_ui.utils.component_registry import registry


class Command(BaseCommand):
    """Comando para gerenciar componentes UI"""
    
    help = 'Gerencia componentes de interface do usuário'
    
    def add_arguments(self, parser):
        """Adiciona argumentos ao comando"""
        subparsers = parser.add_subparsers(dest='action', help='Ações disponíveis')
        
        # Subcomando: list
        list_parser = subparsers.add_parser('list', help='Lista componentes disponíveis')
        list_parser.add_argument(
            '--category',
            type=str,
            help='Filtra por categoria específica'
        )
        list_parser.add_argument(
            '--folder',
            type=str,
            choices=['ui', 'layout'],
            help='Filtra por pasta específica'
        )
        
        # Subcomando: info
        info_parser = subparsers.add_parser('info', help='Mostra informações de um componente')
        info_parser.add_argument('component', type=str, help='Nome do componente')
        
        # Subcomando: add
        add_parser = subparsers.add_parser('add', help='Adiciona um componente ao projeto')
        add_parser.add_argument('component', type=str, help='Nome do componente')
        add_parser.add_argument(
            '--with-dependencies',
            action='store_true',
            help='Instala dependências automaticamente'
        )
        add_parser.add_argument(
            '--force',
            action='store_true',
            help='Força sobrescrever arquivos existentes'
        )
        
        # Subcomando: icons
        icons_parser = subparsers.add_parser('icons', help='Gerencia ícones do projeto')
        icons_parser.add_argument(
            '--install',
            action='store_true',
            help='Instala todos os ícones SVG'
        )
        icons_parser.add_argument(
            '--count',
            action='store_true',
            help='Mostra quantidade de ícones disponíveis'
        )
    
    def handle(self, *args, **options):
        """Processa o comando"""
        action = options['action']
        
        if action == 'list':
            self.handle_list(options)
        elif action == 'info':
            self.handle_info(options)
        elif action == 'add':
            self.handle_add(options)
        elif action == 'icons':
            self.handle_icons(options)
        else:
            self.print_help()
    
    def handle_list(self, options):
        """Lista componentes disponíveis"""
        category = options.get('category')
        folder = options.get('folder')
        
        if category:
            components = registry.list_by_category(category)
            self.stdout.write(
                self.style.SUCCESS(f'\n📦 Componentes da categoria "{category}":')
            )
        elif folder:
            components = registry.list_by_folder(folder)
            self.stdout.write(
                self.style.SUCCESS(f'\n📁 Componentes da pasta "{folder}":')
            )
        else:
            components = registry.list_all()
            self.stdout.write(
                self.style.SUCCESS('\n📦 Todos os componentes disponíveis:')
            )
        
        if not components:
            self.stdout.write(self.style.WARNING('  Nenhum componente encontrado'))
            return
        
        # Agrupa por categoria
        categories = {}
        for comp in components:
            if comp.category not in categories:
                categories[comp.category] = []
            categories[comp.category].append(comp)
        
        for cat, comps in sorted(categories.items()):
            self.stdout.write(f'\n  {cat.upper()}:')
            for comp in sorted(comps, key=lambda x: x.name):
                icon = "🎨" if comp.folder == "ui" else "📐"
                deps = f' (depende de: {", ".join(comp.dependencies)})' if comp.dependencies else ''
                js_indicator = ' 🔧' if comp.requires_js else ''
                variations = f' [{comp.variations}x]' if comp.variations > 1 else ''
                
                self.stdout.write(
                    f'    {icon} {comp.name}{variations}{js_indicator} - {comp.description}{deps}'
                )
        
        self.stdout.write(f'\n  Total: {len(components)} componentes')
        self.stdout.write(f'  Categorias: {", ".join(registry.get_categories())}')
        self.stdout.write(f'  Pastas: {", ".join(registry.get_folders())}')
    
    def handle_info(self, options):
        """Mostra informações detalhadas de um componente"""
        component_name = options['component']
        component = registry.get(component_name)
        
        if not component:
            raise CommandError(f'Componente "{component_name}" não encontrado')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n📋 Informações do componente "{component.name}":')
        )
        
        # Informações básicas
        self.stdout.write(f'  Descrição: {component.description}')
        self.stdout.write(f'  Categoria: {component.category}')
        self.stdout.write(f'  Pasta: {component.folder}/')
        self.stdout.write(f'  Variações: {component.variations}')
        
        # Dependências
        if component.dependencies:
            self.stdout.write(f'  Dependências: {", ".join(component.dependencies)}')
        else:
            self.stdout.write('  Dependências: Nenhuma')
        
        # JavaScript
        if component.requires_js:
            self.stdout.write('  JavaScript: Necessário')
            if component.js_files:
                self.stdout.write(f'    Arquivos: {", ".join(component.js_files)}')
        else:
            self.stdout.write('  JavaScript: Não necessário')
        
        # Tags
        if component.tags:
            self.stdout.write(f'  Tags: {", ".join(component.tags)}')
        
        # Dependências recursivas
        all_deps = registry.get_dependencies(component_name, recursive=True)
        if all_deps:
            self.stdout.write(f'  Dependências (recursivas): {", ".join(all_deps)}')
        
        # Arquivos JS de dependências
        js_files = registry.get_js_files(component_name)
        if js_files:
            self.stdout.write(f'  Arquivos JS (total): {", ".join(js_files)}')
    
    def handle_add(self, options):
        """Adiciona um componente ao projeto"""
        component_name = options['component']
        with_dependencies = options.get('with_dependencies', False)
        force = options.get('force', False)
        
        component = registry.get(component_name)
        if not component:
            raise CommandError(f'Componente "{component_name}" não encontrado')
        
        # Verifica se o projeto está configurado
        if not self._is_project_configured():
            raise CommandError(
                'Projeto não está configurado.\n' +
                'Execute "python manage.py cazenga init --with-tailwind" primeiro.'
            )
        
        # Coleta componentes a instalar
        components_to_install = [component_name]
        
        if with_dependencies:
            dependencies = registry.get_dependencies(component_name, recursive=True)
            components_to_install.extend(dependencies)
            
            if dependencies:
                self.stdout.write(
                    self.style.WARNING(f'Dependências encontradas: {", ".join(dependencies)}')
                )
        
        # Remove duplicatas mantendo ordem
        seen = set()
        unique_components = []
        for comp in components_to_install:
            if comp not in seen:
                seen.add(comp)
                unique_components.append(comp)
        
        # Instala componentes
        installed_components = []
        for comp_name in unique_components:
            if self._install_component(comp_name, force):
                installed_components.append(comp_name)
        
        if installed_components:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Componentes instalados: {", ".join(installed_components)}')
            )
            
            # Mostra próximos passos
            self._show_next_steps(installed_components)
        else:
            self.stdout.write(
                self.style.WARNING('⚠️ Nenhum componente foi instalado')
            )
    
    def handle_icons(self, options):
        """Gerencia ícones do projeto"""
        install = options.get('install', False)
        count = options.get('count', False)
        
        if count:
            self._count_icons()
        elif install:
            self._install_icons()
        else:
            self.stdout.write(self.style.WARNING('Use --install para instalar ícones ou --count para contar'))
    
    def _is_project_configured(self) -> bool:
        """Verifica se o projeto está configurado com django-tailwind"""
        base_dir = Path(settings.BASE_DIR)
        
        # Deve existir a estrutura do django-tailwind
        required_paths = [
            base_dir / 'cazenga_ui',
            base_dir / 'cazenga_ui' / 'static_src',
            base_dir / 'cazenga_ui' / 'templates',
        ]
        
        return all(path.exists() for path in required_paths)
    
    def _get_project_paths(self):
        """Retorna caminhos da estrutura django-tailwind"""
        base_dir = Path(settings.BASE_DIR)
        
        # Sempre usa estrutura django-tailwind (cazenga_ui/)
        return {
            'templates': base_dir / 'cazenga_ui' / 'templates' / 'components',
            'static_js': base_dir / 'cazenga_ui' / 'static' / 'js',
            'static_icons': base_dir / 'cazenga_ui' / 'static' / 'icons',
        }
    
    def _install_component(self, component_name: str, force: bool = False) -> bool:
        """Instala um componente específico"""
        component = registry.get(component_name)
        if not component:
            self.stdout.write(
                self.style.ERROR(f'❌ Componente "{component_name}" não encontrado')
            )
            return False
        
        # Obter caminhos do projeto
        paths = self._get_project_paths()
        
        # Caminhos de origem e destino
        source_dir = Path(__file__).parent.parent.parent / 'templates_source'
        
        # Caminho de destino baseado na pasta do componente
        if component.folder == 'layout':
            dest_dir = paths['templates'] / 'layout'
        else:
            dest_dir = paths['templates'] / 'ui'
        
        source_path = source_dir / component.folder / f'{component_name}.html'
        dest_path = dest_dir / f'{component_name}.html'
        
        # Verifica se o arquivo de origem existe
        if not source_path.exists():
            self.stdout.write(
                self.style.ERROR(f'❌ Arquivo fonte não encontrado: {source_path}')
            )
            return False
        
        # Verifica se já existe
        if dest_path.exists() and not force:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Componente "{component_name}" já existe. Use --force para sobrescrever')
            )
            return False
        
        # Cria diretórios se não existirem
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Copia arquivo
        try:
            shutil.copy2(source_path, dest_path)
            self.stdout.write(
                self.style.SUCCESS(f'✅ {component_name} instalado em {dest_path}')
            )
            
            # Instala arquivos JS se necessário
            if component.requires_js and component.js_files:
                self._install_js_files(component.js_files, force)
            
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao instalar {component_name}: {e}')
            )
            return False
    
    def _install_js_files(self, js_files: List[str], force: bool = False):
        """Instala arquivos JavaScript"""
        paths = self._get_project_paths()
        source_dir = Path(__file__).parent.parent.parent / 'templates_source' / 'js'
        dest_dir = paths['static_js']
        
        for js_file in js_files:
            source_path = source_dir / js_file
            dest_path = dest_dir / js_file
            
            if not source_path.exists():
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Arquivo JS não encontrado: {source_path}')
                )
                continue
            
            if dest_path.exists() and not force:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Arquivo JS já existe: {js_file}')
                )
                continue
            
            try:
                # Cria diretório se não existe
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, dest_path)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ JS instalado: {js_file}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao instalar JS {js_file}: {e}')
                )
    
    def _count_icons(self):
        """Conta ícones disponíveis"""
        icons_dir = Path(__file__).parent.parent.parent / 'templates_source' / 'icons'
        
        if not icons_dir.exists():
            self.stdout.write(self.style.ERROR('❌ Diretório de ícones não encontrado'))
            return
        
        icon_files = list(icons_dir.glob('*.svg'))
        self.stdout.write(
            self.style.SUCCESS(f'📊 Ícones disponíveis: {len(icon_files)}')
        )
        
        # Mostra alguns exemplos
        if icon_files:
            examples = [f.stem for f in icon_files[:10]]
            self.stdout.write(f'   Exemplos: {", ".join(examples)}')
            if len(icon_files) > 10:
                self.stdout.write(f'   ... e mais {len(icon_files) - 10} ícones')
    
    def _install_icons(self):
        """Instala todos os ícones SVG"""
        if not self._is_project_configured():
            raise CommandError(
                'Projeto não está configurado.\n' +
                'Execute "python manage.py cazenga init --with-tailwind" primeiro.'
            )
        
        paths = self._get_project_paths()
        source_dir = Path(__file__).parent.parent.parent / 'templates_source' / 'icons'
        dest_dir = paths['static_icons']
        
        if not source_dir.exists():
            raise CommandError('Diretório de ícones não encontrado')
        
        # Cria diretório de destino
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Copia todos os ícones
        icon_files = list(source_dir.glob('*.svg'))
        copied_count = 0
        
        for icon_file in icon_files:
            dest_path = dest_dir / icon_file.name
            
            try:
                shutil.copy2(icon_file, dest_path)
                copied_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao copiar {icon_file.name}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {copied_count} ícones instalados em {dest_dir}')
        )
        
        # Mostra como usar
        self.stdout.write('\n📋 Como usar os ícones:')
        self.stdout.write('   1. Carregue as template tags: {% load icon_tags %}')
        self.stdout.write('   2. Use o ícone: {% icon "check" %}')
        self.stdout.write('   3. Com classes CSS: {% icon "check" class="w-4 h-4" %}')
    
    def _show_next_steps(self, installed_components: List[str]):
        """Mostra próximos passos após instalação"""
        self.stdout.write('\n📋 Próximos passos:')
        
        # Verifica se há componentes com JS
        has_js = any(
            registry.get(comp).requires_js for comp in installed_components
            if registry.get(comp)
        )
        
        if has_js:
            self.stdout.write('   1. Certifique-se de que o Alpine.js está carregado no template base')
            self.stdout.write('   2. Verifique se os arquivos JS foram copiados para cazenga_ui/static/js/')
        
        # Mostra como usar componentes
        self.stdout.write('   3. Use os componentes em seus templates:')
        
        for comp in installed_components:
            component = registry.get(comp)
            if component:
                folder = component.folder
                # Com django-tailwind, sempre dentro de cazenga_ui
                template_tag = f'{{% include "components/{folder}/{comp}.html" %}}'
                self.stdout.write(f'      {template_tag}')
        
        self.stdout.write('\n   💡 Para usar o template base do django-tailwind:')
        self.stdout.write('      {% extends "base.html" %}')
        
        self.stdout.write('\n   4. Personalize os estilos conforme necessário')
        self.stdout.write('   5. Execute: python manage.py tailwind build')
        self.stdout.write('   6. Para desenvolvimento: python manage.py tailwind start')
    
    def print_help(self):
        """Mostra ajuda do comando"""
        self.stdout.write(
            self.style.SUCCESS('\n🎨 Django Cazenga UI - Comando UI\n')
        )
        
        self.stdout.write('Uso: python manage.py ui <ação> [opções]\n')
        
        self.stdout.write('Ações disponíveis:')
        self.stdout.write('  list              Lista todos os componentes')
        self.stdout.write('  list --category   Lista componentes por categoria')
        self.stdout.write('  list --folder     Lista componentes por pasta (ui/layout)')
        self.stdout.write('  info <componente> Mostra informações detalhadas')
        self.stdout.write('  add <componente>  Adiciona componente ao projeto')
        self.stdout.write('  add --with-dependencies  Instala com dependências')
        self.stdout.write('  icons --install   Instala todos os ícones SVG')
        self.stdout.write('  icons --count     Conta ícones disponíveis')
        
        self.stdout.write('\nExemplos:')
        self.stdout.write('  python manage.py ui list')
        self.stdout.write('  python manage.py ui list --folder ui')
        self.stdout.write('  python manage.py ui info button')
        self.stdout.write('  python manage.py ui add button')
        self.stdout.write('  python manage.py ui add form --with-dependencies')
        self.stdout.write('  python manage.py ui icons --install')
        
        self.stdout.write('\n💡 Estrutura dos componentes (django-tailwind):')
        self.stdout.write('  📁 cazenga_ui/templates/components/ui/     (componentes UI)')
        self.stdout.write('  📁 cazenga_ui/templates/components/layout/ (componentes Layout)')
        self.stdout.write('  📁 cazenga_ui/static/js/                   (arquivos JavaScript)')
        self.stdout.write('  📁 cazenga_ui/static/icons/                (ícones SVG)')
        self.stdout.write('  📁 cazenga_ui/static_src/src/              (CSS fonte - temas)')
        
        self.stdout.write('\n⚠️ Pré-requisito:')
        self.stdout.write('  Execute primeiro: python manage.py cazenga init --with-tailwind') 