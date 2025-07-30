"""
Testes para o comando UI do Django Cazenga UI
"""
import os
import tempfile
import shutil
from io import StringIO
from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.core.management import call_command
from django.core.management.base import CommandError

from cazenga_ui.management.commands.ui import Command as UICommand
from cazenga_ui.utils import registry


class UICommandTestCase(TestCase):
    """Testes para o comando manage.py ui"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.ui_dir = os.path.join(self.temp_dir, 'templates', 'components', 'ui')
        self.js_dir = os.path.join(self.temp_dir, 'static', 'js')
        os.makedirs(self.ui_dir, exist_ok=True)
        os.makedirs(self.js_dir, exist_ok=True)
    
    def tearDown(self):
        """Limpeza após cada teste"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_list_command(self):
        """Testa o comando 'ui list'"""
        out = StringIO()
        call_command('ui', 'list', stdout=out)
        output = out.getvalue()
        
        # Verifica se os componentes aparecem na listagem
        self.assertIn('BASIC', output)
        self.assertIn('button', output)
        self.assertIn('FORM', output)
        self.assertIn('input', output)
    
    def test_list_command_with_category(self):
        """Testa o comando 'ui list' com filtro por categoria"""
        out = StringIO()
        call_command('ui', 'list', '--category', 'form', stdout=out)
        output = out.getvalue()
        
        # Verifica se apenas componentes da categoria 'form' aparecem
        self.assertIn('FORM', output)
        self.assertIn('input', output)
        self.assertNotIn('BASIC', output)
    
    def test_list_command_invalid_category(self):
        """Testa o comando 'ui list' com categoria inválida"""
        out = StringIO()
        call_command('ui', 'list', '--category', 'categoria-inexistente', stdout=out)
        output = out.getvalue()
        
        self.assertIn('Nenhum componente encontrado', output)
        self.assertIn('Categorias disponíveis', output)
    
    def test_info_command(self):
        """Testa o comando 'ui info' para um componente específico"""
        out = StringIO()
        call_command('ui', 'info', 'button', stdout=out)
        output = out.getvalue()
        
        # Verifica informações do componente button
        self.assertIn('Componente: button', output)
        self.assertIn('Descrição:', output)
        self.assertIn('Categoria:', output)
        self.assertIn('Variações:', output)
    
    def test_info_command_invalid_component(self):
        """Testa o comando 'ui info' para componente inexistente"""
        with self.assertRaises(CommandError) as cm:
            call_command('ui', 'info', 'componente-inexistente')
        
        self.assertIn('não encontrado', str(cm.exception))
    
    def test_info_command_no_component(self):
        """Testa o comando 'ui info' sem especificar componente"""
        with self.assertRaises(CommandError) as cm:
            call_command('ui', 'info')
        
        self.assertIn('deve fornecer um nome', str(cm.exception))
    
    @override_settings(BASE_DIR=tempfile.mkdtemp())
    @patch('cazenga_ui.management.commands.ui.TEMPLATES_SOURCE_DIR')
    @patch('cazenga_ui.management.commands.ui.JS_SOURCE_DIR')
    def test_add_command_simple_component(self, mock_js_dir, mock_templates_dir):
        """Testa adicionar um componente simples"""
        # Configurar mocks
        mock_templates_dir = tempfile.mkdtemp()
        mock_js_dir = tempfile.mkdtemp()
        
        # Criar arquivo de template fictício
        template_file = os.path.join(mock_templates_dir, 'button.html')
        with open(template_file, 'w') as f:
            f.write('<button>{{ text }}</button>')
        
        with patch('cazenga_ui.management.commands.ui.TEMPLATES_SOURCE_DIR', mock_templates_dir), \
             patch('cazenga_ui.management.commands.ui.JS_SOURCE_DIR', mock_js_dir), \
             patch('cazenga_ui.management.commands.ui.settings.BASE_DIR', self.temp_dir):
            
            out = StringIO()
            call_command('ui', 'add', 'button', stdout=out)
            output = out.getvalue()
            
            # Verificar se o arquivo foi copiado
            destination_file = os.path.join(self.ui_dir, 'button.html')
            self.assertTrue(os.path.exists(destination_file))
            
            # Verificar output
            self.assertIn('instalados com sucesso', output)
            self.assertIn('button.html', output)
        
        # Limpeza
        shutil.rmtree(mock_templates_dir)
        shutil.rmtree(mock_js_dir)
    
    @patch('builtins.input', return_value='n')
    @override_settings(BASE_DIR=tempfile.mkdtemp())
    @patch('cazenga_ui.management.commands.ui.TEMPLATES_SOURCE_DIR')
    def test_add_command_existing_component_no_overwrite(self, mock_templates_dir, mock_input):
        """Testa adicionar componente que já existe - usuário escolhe não sobrescrever"""
        # Configurar mock
        mock_templates_dir = tempfile.mkdtemp()
        
        # Criar arquivo de template fictício
        template_file = os.path.join(mock_templates_dir, 'button.html')
        with open(template_file, 'w') as f:
            f.write('<button>{{ text }}</button>')
        
        # Criar arquivo existente no destino
        existing_file = os.path.join(self.ui_dir, 'button.html')
        with open(existing_file, 'w') as f:
            f.write('<button>Existing</button>')
        
        with patch('cazenga_ui.management.commands.ui.TEMPLATES_SOURCE_DIR', mock_templates_dir), \
             patch('cazenga_ui.management.commands.ui.settings.BASE_DIR', self.temp_dir):
            
            out = StringIO()
            call_command('ui', 'add', 'button', stdout=out)
            output = out.getvalue()
            
            # Verificar se operação foi cancelada
            self.assertIn('cancelada', output)
            
            # Verificar se arquivo não foi alterado
            with open(existing_file, 'r') as f:
                content = f.read()
            self.assertEqual(content, '<button>Existing</button>')
        
        # Limpeza
        shutil.rmtree(mock_templates_dir)
    
    def test_icons_list_command(self):
        """Testa o comando 'ui icons --list-icons'"""
        out = StringIO()
        call_command('ui', 'icons', '--list-icons', stdout=out)
        output = out.getvalue()
        
        # Verifica se mostra informações sobre ícones
        self.assertIn('Ícones disponíveis', output)
        self.assertIn('check', output)  # Ícone que sabemos que existe
    
    @override_settings(BASE_DIR=tempfile.mkdtemp())
    @patch('cazenga_ui.management.commands.ui.ICONS_SOURCE_DIR')
    def test_icons_install_specific(self, mock_icons_dir):
        """Testa instalar um ícone específico"""
        # Configurar mock
        mock_icons_dir = tempfile.mkdtemp()
        
        # Criar ícone fictício
        icon_file = os.path.join(mock_icons_dir, 'check.svg')
        with open(icon_file, 'w') as f:
            f.write('<svg>check icon</svg>')
        
        with patch('cazenga_ui.management.commands.ui.ICONS_SOURCE_DIR', mock_icons_dir), \
             patch('cazenga_ui.management.commands.ui.settings.BASE_DIR', self.temp_dir):
            
            out = StringIO()
            call_command('ui', 'icons', 'check', stdout=out)
            output = out.getvalue()
            
            # Verificar se ícone foi instalado
            icons_dir = os.path.join(self.temp_dir, 'templates', 'components', 'icons')
            destination_file = os.path.join(icons_dir, 'check.svg')
            self.assertTrue(os.path.exists(destination_file))
            
            # Verificar output
            self.assertIn('check.svg', output)
            self.assertIn('instalado', output)
        
        # Limpeza
        shutil.rmtree(mock_icons_dir)


class ComponentRegistryTestCase(TestCase):
    """Testes para o registro de componentes"""
    
    def test_registry_has_components(self):
        """Verifica se o registry tem componentes carregados"""
        components = registry.list_all()
        self.assertGreater(len(components), 0)
        
        # Verifica se componentes essenciais estão presentes
        component_names = [c.name for c in components]
        self.assertIn('button', component_names)
        self.assertIn('input', component_names)
        self.assertIn('card', component_names)
    
    def test_get_component(self):
        """Testa obter um componente específico"""
        button = registry.get('button')
        self.assertIsNotNone(button)
        self.assertEqual(button.name, 'button')
        self.assertEqual(button.category, 'basic')
        
        # Testa componente inexistente
        inexistente = registry.get('componente-inexistente')
        self.assertIsNone(inexistente)
    
    def test_list_by_category(self):
        """Testa listar componentes por categoria"""
        form_components = registry.list_by_category('form')
        self.assertGreater(len(form_components), 0)
        
        # Verifica se todos são da categoria 'form'
        for component in form_components:
            self.assertEqual(component.category, 'form')
    
    def test_get_categories(self):
        """Testa obter todas as categorias"""
        categories = registry.get_categories()
        self.assertGreater(len(categories), 0)
        self.assertIn('basic', categories)
        self.assertIn('form', categories)
        self.assertIn('navigation', categories)
    
    def test_get_dependencies(self):
        """Testa obter dependências de um componente"""
        # Testa componente sem dependências
        deps = registry.get_dependencies('button')
        self.assertEqual(deps, [])
        
        # Testa componente com dependências (se houver)
        form_deps = registry.get_dependencies('form')
        # Como o form depende de input e button, deve retornar essas dependências
        self.assertIsInstance(form_deps, list)
    
    def test_get_js_files(self):
        """Testa obter arquivos JS de um componente"""
        # Testa componente sem JS
        js_files = registry.get_js_files('button')
        self.assertEqual(js_files, [])
        
        # Testa componente com JS específico
        sidebar_js = registry.get_js_files('sidebar')
        if sidebar_js:  # Se o sidebar tem JS configurado
            self.assertIn('sidebar-highlight.js', sidebar_js) 