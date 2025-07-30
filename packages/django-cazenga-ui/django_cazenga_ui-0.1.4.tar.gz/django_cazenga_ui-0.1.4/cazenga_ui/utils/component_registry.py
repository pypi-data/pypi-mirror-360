"""
Component Registry para Django Cazenga UI
Registra todos os componentes disponíveis com seus metadados
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class Component:
    """Define um componente com seus metadados"""
    name: str
    description: str
    category: str
    folder: str = "ui"  # "ui" ou "layout"
    dependencies: List[str] = None
    requires_js: bool = False
    js_files: List[str] = None
    variations: int = 1
    tags: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.js_files is None:
            self.js_files = []
        if self.tags is None:
            self.tags = []


class ComponentRegistry:
    """Registro central de todos os componentes disponíveis"""
    
    def __init__(self):
        self._components: Dict[str, Component] = {}
        self._initialize_registry()
    
    def _initialize_registry(self):
        """Inicializa o registro com todos os componentes disponíveis"""
        
        # Componentes Básicos (UI)
        self.register(Component(
            name="button",
            description="Botão interativo com múltiplas variantes e tamanhos",
            category="basic",
            folder="ui",
            variations=9,
            tags=["form", "interactive", "action"]
        ))
        
        self.register(Component(
            name="card",
            description="Container de conteúdo com header, body e footer",
            category="basic",
            folder="ui",
            variations=3,
            tags=["container", "layout"]
        ))
        
        self.register(Component(
            name="badge",
            description="Pequeno rótulo para status e categorização",
            category="display",
            folder="ui",
            variations=5,
            tags=["status", "label"]
        ))
        
        self.register(Component(
            name="avatar",
            description="Exibe imagem de perfil ou iniciais",
            category="display",
            folder="ui",
            variations=4,
            tags=["user", "profile", "image"]
        ))
        
        # Componentes de Formulário (UI)
        self.register(Component(
            name="input",
            description="Campo de entrada de texto com validação",
            category="form",
            folder="ui",
            variations=7,
            tags=["form", "input", "text"]
        ))
        
        self.register(Component(
            name="textarea",
            description="Campo de texto multilinha",
            category="form",
            folder="ui",
            variations=4,
            tags=["form", "input", "text", "multiline"]
        ))
        
        self.register(Component(
            name="checkbox",
            description="Caixa de seleção múltipla",
            category="form",
            folder="ui",
            variations=4,
            tags=["form", "input", "selection"]
        ))
        
        self.register(Component(
            name="radio-group",
            description="Grupo de opções exclusivas",
            category="form",
            folder="ui",
            variations=3,
            tags=["form", "input", "selection"]
        ))
        
        self.register(Component(
            name="select",
            description="Lista suspensa para seleção",
            category="form",
            folder="ui",
            variations=6,
            requires_js=True,
            tags=["form", "input", "dropdown"]
        ))
        
        self.register(Component(
            name="switch",
            description="Alternador binário on/off",
            category="form",
            folder="ui",
            variations=3,
            tags=["form", "input", "toggle"]
        ))
        
        self.register(Component(
            name="form",
            description="Container de formulário com validação",
            category="form",
            folder="ui",
            dependencies=["input", "button"],
            variations=3,
            tags=["form", "container", "validation"]
        ))
        
        self.register(Component(
            name="label",
            description="Rótulo para campos de formulário",
            category="form",
            folder="ui",
            variations=2,
            tags=["form", "text"]
        ))
        
        # Componentes de Navegação (UI)
        self.register(Component(
            name="breadcrumb",
            description="Trilha de navegação hierárquica",
            category="navigation",
            folder="ui",
            variations=3,
            tags=["navigation", "hierarchy"]
        ))
        
        self.register(Component(
            name="pagination",
            description="Navegação entre páginas de conteúdo",
            category="navigation",
            folder="ui",
            variations=4,
            tags=["navigation", "pages"]
        ))
        
        self.register(Component(
            name="tabs",
            description="Navegação em abas com conteúdo alternável",
            category="navigation",
            folder="ui",
            requires_js=True,
            variations=4,
            tags=["navigation", "interactive", "container"]
        ))
        
        self.register(Component(
            name="navigation-menu",
            description="Menu de navegação principal com submenus",
            category="navigation",
            folder="ui",
            requires_js=True,
            variations=5,
            tags=["navigation", "menu", "dropdown"]
        ))
        
        self.register(Component(
            name="sidebar",
            description="Painel lateral de navegação",
            category="navigation",
            folder="ui",
            requires_js=True,
            js_files=["sidebar-highlight.js"],
            variations=5,
            tags=["navigation", "layout", "menu"]
        ))
        
        self.register(Component(
            name="menubar",
            description="Barra de menu horizontal",
            category="navigation",
            folder="ui",
            requires_js=True,
            variations=4,
            tags=["navigation", "menu", "toolbar"]
        ))
        
        # Componentes de Feedback (UI)
        self.register(Component(
            name="alert",
            description="Mensagem de alerta ou notificação",
            category="feedback",
            folder="ui",
            variations=5,
            tags=["feedback", "notification", "message"]
        ))
        
        self.register(Component(
            name="progress",
            description="Indicador de progresso linear",
            category="feedback",
            folder="ui",
            variations=4,
            tags=["feedback", "loading", "status"]
        ))
        
        self.register(Component(
            name="skeleton",
            description="Placeholder animado para conteúdo carregando",
            category="feedback",
            folder="ui",
            variations=5,
            tags=["feedback", "loading", "placeholder"]
        ))
        
        self.register(Component(
            name="spinner",
            description="Indicador de carregamento circular",
            category="feedback",
            folder="ui",
            variations=6,
            tags=["feedback", "loading"]
        ))
        
        self.register(Component(
            name="sonner",
            description="Sistema de notificações toast",
            category="feedback",
            folder="ui",
            requires_js=True,
            variations=8,
            tags=["feedback", "notification", "toast"]
        ))
        
        # Componentes de Overlay (UI)
        self.register(Component(
            name="dialog",
            description="Janela modal para interações focadas",
            category="overlay",
            folder="ui",
            requires_js=True,
            dependencies=["button"],
            variations=5,
            tags=["overlay", "modal", "interactive"]
        ))
        
        self.register(Component(
            name="alert-dialog",
            description="Dialog de confirmação de ações",
            category="overlay",
            folder="ui",
            requires_js=True,
            dependencies=["dialog", "button"],
            variations=3,
            tags=["overlay", "modal", "confirmation"]
        ))
        
        self.register(Component(
            name="drawer",
            description="Painel deslizante lateral",
            category="overlay",
            folder="ui",
            requires_js=True,
            variations=3,
            tags=["overlay", "panel", "slide"]
        ))
        
        self.register(Component(
            name="modal",
            description="Janela modal simples",
            category="overlay",
            folder="ui",
            requires_js=True,
            variations=5,
            tags=["overlay", "modal"]
        ))
        
        self.register(Component(
            name="sheet",
            description="Painel deslizante inferior ou lateral",
            category="overlay",
            folder="ui",
            requires_js=True,
            variations=4,
            tags=["overlay", "panel", "slide"]
        ))
        
        self.register(Component(
            name="popover",
            description="Popup contextual flutuante",
            category="overlay",
            folder="ui",
            requires_js=True,
            variations=5,
            tags=["overlay", "popup", "contextual"]
        ))
        
        self.register(Component(
            name="tooltip",
            description="Dica contextual ao passar o mouse",
            category="overlay",
            folder="ui",
            requires_js=True,
            variations=4,
            tags=["overlay", "hint", "contextual"]
        ))
        
        # Componentes Interativos (UI)
        self.register(Component(
            name="accordion",
            description="Lista expansível de seções",
            category="interactive",
            folder="ui",
            requires_js=True,
            variations=4,
            tags=["interactive", "collapse", "list"]
        ))
        
        self.register(Component(
            name="carousel",
            description="Apresentação de slides/imagens",
            category="interactive",
            folder="ui",
            requires_js=True,
            variations=3,
            tags=["interactive", "slider", "gallery"]
        ))
        
        self.register(Component(
            name="collapsible",
            description="Seção expansível/recolhível",
            category="interactive",
            folder="ui",
            requires_js=True,
            variations=3,
            tags=["interactive", "collapse"]
        ))
        
        self.register(Component(
            name="command",
            description="Paleta de comandos com busca",
            category="interactive",
            folder="ui",
            requires_js=True,
            variations=5,
            tags=["interactive", "search", "command"]
        ))
        
        self.register(Component(
            name="context-menu",
            description="Menu contextual com clique direito",
            category="interactive",
            folder="ui",
            requires_js=True,
            variations=3,
            tags=["interactive", "menu", "contextual"]
        ))
        
        self.register(Component(
            name="dropdown",
            description="Menu suspenso básico",
            category="interactive",
            folder="ui",
            requires_js=True,
            variations=5,
            tags=["interactive", "menu", "dropdown"]
        ))
        
        self.register(Component(
            name="dropdown-menu",
            description="Menu suspenso avançado com ações",
            category="interactive",
            folder="ui",
            requires_js=True,
            dependencies=["dropdown"],
            variations=4,
            tags=["interactive", "menu", "dropdown", "actions"]
        ))
        
        self.register(Component(
            name="hover-card",
            description="Card informativo ao passar o mouse",
            category="interactive",
            folder="ui",
            requires_js=True,
            dependencies=["card"],
            variations=4,
            tags=["interactive", "hover", "info"]
        ))
        
        self.register(Component(
            name="toggle",
            description="Botão de alternância",
            category="interactive",
            folder="ui",
            requires_js=True,
            variations=4,
            tags=["interactive", "toggle", "button"]
        ))
        
        self.register(Component(
            name="toggle-group",
            description="Grupo de botões de alternância",
            category="interactive",
            folder="ui",
            requires_js=True,
            dependencies=["toggle"],
            variations=3,
            tags=["interactive", "toggle", "group"]
        ))
        
        # Componentes de Dados (UI)
        self.register(Component(
            name="table",
            description="Tabela de dados com ordenação e filtros",
            category="data",
            folder="ui",
            requires_js=True,
            variations=5,
            tags=["data", "table", "grid"]
        ))
        
        self.register(Component(
            name="chart",
            description="Gráficos e visualizações de dados",
            category="data",
            folder="ui",
            requires_js=True,
            variations=4,
            tags=["data", "chart", "visualization"]
        ))
        
        self.register(Component(
            name="calendar",
            description="Seletor de data e calendário",
            category="data",
            folder="ui",
            requires_js=True,
            variations=5,
            tags=["data", "date", "calendar", "picker"]
        ))
        
        # Componentes de Layout (LAYOUT FOLDER)
        self.register(Component(
            name="layout",
            description="Estruturas de layout de página",
            category="layout",
            folder="layout",
            dependencies=["sidebar"],
            variations=4,
            tags=["layout", "structure", "page"]
        ))
        
        # Componentes Utilitários (UI)
        self.register(Component(
            name="separator",
            description="Linha divisória visual",
            category="utility",
            folder="ui",
            variations=2,
            tags=["layout", "divider"]
        ))
        
        self.register(Component(
            name="aspect-ratio",
            description="Container com proporção fixa",
            category="utility",
            folder="ui",
            variations=3,
            tags=["layout", "ratio", "container"]
        ))
        
        self.register(Component(
            name="scroll-area",
            description="Área com scroll customizado",
            category="utility",
            folder="ui",
            requires_js=True,
            variations=6,
            tags=["layout", "scroll", "container"]
        ))
        
        self.register(Component(
            name="resizable",
            description="Painéis redimensionáveis",
            category="utility",
            folder="ui",
            requires_js=True,
            variations=5,
            tags=["layout", "resize", "panel"]
        ))
        
        # Componentes Especializados (UI)
        self.register(Component(
            name="input-otp",
            description="Input para códigos OTP/PIN",
            category="specialized",
            folder="ui",
            requires_js=True,
            variations=7,
            tags=["form", "security", "otp", "code"]
        ))
        
        self.register(Component(
            name="slider",
            description="Controle deslizante para valores",
            category="specialized",
            folder="ui",
            requires_js=True,
            variations=6,
            tags=["form", "input", "range", "slider"]
        ))
        
        self.register(Component(
            name="text-editor",
            description="Editor de texto rico completo",
            category="specialized",
            folder="ui",
            requires_js=True,
            variations=6,
            tags=["editor", "wysiwyg", "text", "content"]
        ))
        
        self.register(Component(
            name="content-manager",
            description="Sistema de gestão de conteúdo",
            category="specialized",
            folder="ui",
            requires_js=True,
            dependencies=["text-editor", "form", "button", "card"],
            variations=4,
            tags=["cms", "content", "management", "editor"]
        ))
        
        # Componente especial de ícone (UI)
        self.register(Component(
            name="icon",
            description="Sistema de ícones SVG",
            category="utility",
            folder="ui",
            variations=1,
            tags=["icon", "svg", "utility"]
        ))
    
    def register(self, component: Component):
        """Registra um componente"""
        self._components[component.name] = component
    
    def get(self, name: str) -> Optional[Component]:
        """Obtém um componente pelo nome"""
        return self._components.get(name)
    
    def list_all(self) -> List[Component]:
        """Lista todos os componentes"""
        return list(self._components.values())
    
    def list_by_category(self, category: str) -> List[Component]:
        """Lista componentes por categoria"""
        return [c for c in self._components.values() if c.category == category]
    
    def list_by_folder(self, folder: str) -> List[Component]:
        """Lista componentes por pasta (ui ou layout)"""
        return [c for c in self._components.values() if c.folder == folder]
    
    def get_categories(self) -> List[str]:
        """Obtém todas as categorias únicas"""
        categories = set(c.category for c in self._components.values())
        return sorted(list(categories))
    
    def get_folders(self) -> List[str]:
        """Obtém todas as pastas únicas"""
        folders = set(c.folder for c in self._components.values())
        return sorted(list(folders))
    
    def get_dependencies(self, component_name: str, recursive: bool = True) -> List[str]:
        """Obtém todas as dependências de um componente"""
        component = self.get(component_name)
        if not component:
            return []
        
        dependencies = set(component.dependencies)
        
        if recursive:
            for dep in list(dependencies):
                sub_deps = self.get_dependencies(dep, recursive=True)
                dependencies.update(sub_deps)
        
        return sorted(list(dependencies))
    
    def get_js_files(self, component_name: str) -> List[str]:
        """Obtém arquivos JS necessários para um componente e suas dependências"""
        all_components = [component_name] + self.get_dependencies(component_name)
        js_files = []
        
        for comp_name in all_components:
            component = self.get(comp_name)
            if component and component.js_files:
                js_files.extend(component.js_files)
        
        # Remove duplicatas mantendo ordem
        seen = set()
        unique_files = []
        for file in js_files:
            if file not in seen:
                seen.add(file)
                unique_files.append(file)
        
        return unique_files


# Instância global do registro
registry = ComponentRegistry() 