import os
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def svg_icon(name, size="size-6", css_class=""):
    """
    Carrega um ícone SVG da pasta icons e retorna o conteúdo inline.
    
    Args:
        name: Nome do ícone (sem extensão .svg)
        size: Classe de tamanho Tailwind (ex: size-6, size-4)
        css_class: Classes CSS adicionais
    
    Usage:
        {% svg_icon "heart" "size-8" "text-red-500" %}
    """
    if not name:
        # Ícone padrão quando name não é fornecido
        return mark_safe(f'''
            <svg class="{size} {css_class}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 15 15">
                <circle cx="7.5" cy="7.5" r="4.5" fill="currentColor"/>
            </svg>
        ''')
    
    # Caminho para o arquivo SVG
    icon_path = os.path.join(settings.BASE_DIR, 'theme', 'static', 'icons', f'{name}.svg')
    
    try:
        # Ler o conteúdo do arquivo SVG
        with open(icon_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        
        # Adicionar classes CSS ao SVG
        # Procurar pela tag <svg> e adicionar as classes
        if '<svg' in svg_content:
            # Encontrar a posição da tag svg
            svg_start = svg_content.find('<svg')
            svg_end = svg_content.find('>', svg_start)
            
            if svg_end != -1:
                # Extrair a tag svg atual
                svg_tag = svg_content[svg_start:svg_end]
                
                # Adicionar classes CSS
                classes = f'class="{size} {css_class}"'
                
                # Se já tem class, substituir, senão adicionar
                if 'class=' in svg_tag:
                    # Substituir classe existente
                    import re
                    svg_tag = re.sub(r'class="[^"]*"', classes, svg_tag)
                else:
                    # Adicionar classe
                    svg_tag = svg_tag + f' {classes}'
                
                # Reconstruir o SVG
                svg_content = svg_content[:svg_start] + svg_tag + svg_content[svg_end:]
        
        return mark_safe(svg_content)
        
    except FileNotFoundError:
        # Se o arquivo não existir, retornar ícone padrão
        return mark_safe(f'''
            <svg class="{size} {css_class}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 15 15">
                <circle cx="7.5" cy="7.5" r="4.5" fill="currentColor"/>
            </svg>
        ''')
    except Exception as e:
        # Em caso de erro, retornar ícone padrão
        return mark_safe(f'''
            <svg class="{size} {css_class}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 15 15">
                <circle cx="7.5" cy="7.5" r="4.5" fill="currentColor"/>
            </svg>
        ''')

@register.simple_tag
def icon(name, size="size-6", **kwargs):
    """
    Alias para svg_icon para compatibilidade.
    
    Args:
        name: Nome do ícone (sem extensão .svg)
        size: Classe de tamanho Tailwind (ex: size-6, size-4)
        **kwargs: Argumentos adicionais incluindo 'class' para classes CSS
    
    Usage:
        {% icon "heart" "size-8" class="text-red-500" %}
    """
    css_class = kwargs.get('class', '')
    return svg_icon(name, size, css_class)

@register.simple_tag
def icon_exists(name):
    """
    Verifica se um ícone existe na pasta icons.
    
    Args:
        name: Nome do ícone (sem extensão .svg)
    
    Returns:
        bool: True se o ícone existe, False caso contrário
    """
    if not name:
        return False
    
    icon_path = os.path.join(settings.BASE_DIR, 'theme', 'static', 'icons', f'{name}.svg')
    return os.path.exists(icon_path) 