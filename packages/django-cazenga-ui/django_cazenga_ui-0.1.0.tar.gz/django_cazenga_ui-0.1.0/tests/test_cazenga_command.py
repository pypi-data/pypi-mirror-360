"""
Testes para o comando cazenga do Django Cazenga UI
"""
import os
import tempfile
import shutil
from io import StringIO
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.core.management import call_command
from django.core.management.base import CommandError


class CazengaCommandTestCase(TestCase):
    """Testes para o comando manage.py cazenga"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Limpeza após cada teste"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @override_settings(INSTALLED_APPS=['cazenga_ui'], BASE_DIR=tempfile.mkdtemp())
    def test_init_command_creates_directories(self):
        """Testa se o comando init cria a estrutura de diretórios"""
        with patch('cazenga_ui.management.commands.cazenga.settings.BASE_DIR', self.temp_dir):
            out = StringIO()
            call_command('cazenga', 'init', stdout=out)
            output = out.getvalue()
            
            # Verificar se diretórios foram criados
            expected_dirs = [
                os.path.join(self.temp_dir, 'templates'),
                os.path.join(self.temp_dir, 'templates', 'components'),
                os.path.join(self.temp_dir, 'templates', 'components', 'ui'),
                os.path.join(self.temp_dir, 'static'),
                os.path.join(self.temp_dir, 'static', 'js'),
            ]
            
            for dir_path in expected_dirs:
                self.assertTrue(os.path.exists(dir_path), f"Diretório {dir_path} não foi criado")
            
            # Verificar output
            self.assertIn('Iniciando configuração', output)
            self.assertIn('Criando estrutura', output)
    
    @override_settings(INSTALLED_APPS=['cazenga_ui'], BASE_DIR=tempfile.mkdtemp())
    def test_init_command_creates_base_template(self):
        """Testa se o comando init cria o template base.html"""
        with patch('cazenga_ui.management.commands.cazenga.settings.BASE_DIR', self.temp_dir):
            out = StringIO()
            call_command('cazenga', 'init', stdout=out)
            
            # Verificar se base.html foi criado
            base_template_path = os.path.join(self.temp_dir, 'templates', 'base.html')
            self.assertTrue(os.path.exists(base_template_path))
            
            # Verificar conteúdo do template
            with open(base_template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.assertIn('<!DOCTYPE html>', content)
            self.assertIn('Alpine.js', content)
            self.assertIn('tailwindcss', content)
            self.assertIn('{% block content %}', content)
    
    @override_settings(INSTALLED_APPS=['cazenga_ui'], BASE_DIR=tempfile.mkdtemp())
    def test_init_command_creates_theme_css(self):
        """Testa se o comando init cria o arquivo de tema CSS"""
        with patch('cazenga_ui.management.commands.cazenga.settings.BASE_DIR', self.temp_dir):
            out = StringIO()
            call_command('cazenga', 'init', stdout=out)
            
            # Verificar se arquivo CSS foi criado
            css_path = os.path.join(self.temp_dir, 'static', 'css', 'cazenga-theme.css')
            self.assertTrue(os.path.exists(css_path))
            
            # Verificar conteúdo do CSS
            with open(css_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.assertIn('@layer base', content)
            self.assertIn('--background:', content)
            self.assertIn('--primary:', content)
            self.assertIn('.dark', content)
    
    @override_settings(INSTALLED_APPS=['cazenga_ui'], BASE_DIR=tempfile.mkdtemp())
    def test_init_command_skips_existing_base_template(self):
        """Testa se o comando init não sobrescreve template base.html existente"""
        # Criar base.html existente
        templates_dir = os.path.join(self.temp_dir, 'templates')
        os.makedirs(templates_dir, exist_ok=True)
        base_template_path = os.path.join(templates_dir, 'base.html')
        
        existing_content = '<html>Existing template</html>'
        with open(base_template_path, 'w', encoding='utf-8') as f:
            f.write(existing_content)
        
        with patch('cazenga_ui.management.commands.cazenga.settings.BASE_DIR', self.temp_dir):
            out = StringIO()
            call_command('cazenga', 'init', stdout=out)
            
            # Verificar se conteúdo não foi alterado
            with open(base_template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.assertEqual(content, existing_content)
    
    @override_settings(INSTALLED_APPS=['cazenga_ui'], BASE_DIR=tempfile.mkdtemp())
    def test_init_command_shows_final_instructions(self):
        """Testa se o comando init mostra instruções finais"""
        with patch('cazenga_ui.management.commands.cazenga.settings.BASE_DIR', self.temp_dir):
            out = StringIO()
            call_command('cazenga', 'init', stdout=out)
            output = out.getvalue()
            
            # Verificar instruções finais
            self.assertIn('Configuração inicial concluída', output)
            self.assertIn('Próximos passos', output)
            self.assertIn('python manage.py ui list', output)
            self.assertIn('python manage.py ui add button', output)
    
    @override_settings(INSTALLED_APPS=['cazenga_ui'], BASE_DIR=tempfile.mkdtemp())
    def test_init_command_shows_tailwind_config(self):
        """Testa se o comando init mostra configuração do Tailwind"""
        with patch('cazenga_ui.management.commands.cazenga.settings.BASE_DIR', self.temp_dir):
            out = StringIO()
            call_command('cazenga', 'init', stdout=out)
            output = out.getvalue()
            
            # Verificar se mostra configuração do Tailwind
            self.assertIn('Configuração do Tailwind CSS', output)
            self.assertIn('tailwind.config.js', output)
            self.assertIn('content:', output)
    
    @override_settings(INSTALLED_APPS=['other_app'], BASE_DIR=tempfile.mkdtemp())
    def test_init_command_missing_cazenga_ui_in_installed_apps(self):
        """Testa comportamento quando cazenga_ui não está em INSTALLED_APPS"""
        with patch('cazenga_ui.management.commands.cazenga.settings.BASE_DIR', self.temp_dir):
            out = StringIO()
            call_command('cazenga', 'init', stdout=out)
            output = out.getvalue()
            
            # Verificar se mostra aviso
            self.assertIn('não está em INSTALLED_APPS', output)
            self.assertIn('INSTALLED_APPS', output)
    
    @override_settings(INSTALLED_APPS=['cazenga_ui'], BASE_DIR=tempfile.mkdtemp())
    @patch('cazenga_ui.management.commands.cazenga.Command.setup_tailwind')
    def test_init_command_with_tailwind_flag(self, mock_setup_tailwind):
        """Testa comando init com flag --with-tailwind"""
        with patch('cazenga_ui.management.commands.cazenga.settings.BASE_DIR', self.temp_dir):
            out = StringIO()
            call_command('cazenga', 'init', '--with-tailwind', stdout=out)
            
            # Verificar se setup_tailwind foi chamado
            mock_setup_tailwind.assert_called_once()
    
    @override_settings(INSTALLED_APPS=['cazenga_ui'], BASE_DIR=tempfile.mkdtemp())
    @patch('builtins.__import__', side_effect=ImportError())
    def test_init_command_tailwind_not_installed(self, mock_import):
        """Testa comportamento quando django-tailwind não está instalado"""
        with patch('cazenga_ui.management.commands.cazenga.settings.BASE_DIR', self.temp_dir):
            out = StringIO()
            call_command('cazenga', 'init', '--with-tailwind', stdout=out)
            output = out.getvalue()
            
            # Verificar se mostra mensagem sobre django-tailwind não estar instalado
            self.assertIn('não está instalado', output)
            self.assertIn('pip install django-tailwind', output)


class CazengaCommandIntegrationTestCase(TestCase):
    """Testes de integração para o comando cazenga"""
    
    @override_settings(INSTALLED_APPS=['cazenga_ui'], BASE_DIR=tempfile.mkdtemp())
    def test_full_init_workflow(self):
        """Testa o fluxo completo de inicialização"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            with patch('cazenga_ui.management.commands.cazenga.settings.BASE_DIR', temp_dir):
                # Executar comando init
                out = StringIO()
                call_command('cazenga', 'init', stdout=out)
                output = out.getvalue()
                
                # Verificar se todos os arquivos e diretórios foram criados
                expected_files = [
                    os.path.join(temp_dir, 'templates', 'base.html'),
                    os.path.join(temp_dir, 'static', 'css', 'cazenga-theme.css'),
                ]
                
                expected_dirs = [
                    os.path.join(temp_dir, 'templates', 'components', 'ui'),
                    os.path.join(temp_dir, 'static', 'js'),
                ]
                
                for file_path in expected_files:
                    self.assertTrue(os.path.exists(file_path), f"Arquivo {file_path} não foi criado")
                
                for dir_path in expected_dirs:
                    self.assertTrue(os.path.exists(dir_path), f"Diretório {dir_path} não foi criado")
                
                # Verificar se output contém informações esperadas
                self.assertIn('configuração inicial concluída', output.lower())
                
        finally:
            # Limpeza
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir) 