# src/core/content/code.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from .base import ContentObject, ObjectType


@dataclass
class CodeObject(ContentObject):
    """Objeto para código (JavaScript, CSS, etc)."""

    content: str = ""
    language: Optional[str] = None  # javascript, python, css, etc.
    is_inline: bool = False  # inline vs block
    source_file: Optional[str] = None  # arquivo de origem se aplicável

    object_type: str = ObjectType.CODE

    def get_content(self) -> str:
        """Retorna representação textual do código."""
        if self.is_inline:
            return f"`{self.content}`" if self.content else ""
        else:
            lang_label = f" ({self.language})" if self.language else ""
            return f"[CODE{lang_label}]\n{self.content}\n[/CODE]"

    def get_raw_data(self) -> Dict[str, Any]:
        return {
            'content': self.content,
            'language': self.language,
            'is_inline': self.is_inline,
            'source_file': self.source_file,
            'line_count': self.get_line_count(),
            'char_count': len(self.content)
        }

    def get_line_count(self) -> int:
        """Retorna número de linhas do código."""
        return len(self.content.splitlines()) if self.content else 0

    def is_empty(self) -> bool:
        """Verifica se o código está vazio."""
        return not self.content.strip()

    def get_functions(self) -> List[str]:
        """Tenta extrair nomes de funções (básico)."""
        functions = []
        if not self.content:
            return functions

        lines = self.content.splitlines()

        # Padrões básicos por linguagem
        if self.language in ('javascript', 'js'):
            import re
            # function nome(...) ou nome = function(...)
            patterns = [
                r'function\s+(\w+)\s*\(',
                r'(\w+)\s*=\s*function\s*\(',
                r'(\w+)\s*:\s*function\s*\(',
                r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>'
            ]
            for line in lines:
                for pattern in patterns:
                    matches = re.findall(pattern, line)
                    functions.extend(matches)

        elif self.language in ('python', 'py'):
            import re
            pattern = r'def\s+(\w+)\s*\('
            for line in lines:
                matches = re.findall(pattern, line)
                functions.extend(matches)

        return list(set(functions))  # Remove duplicatas

    def get_imports(self) -> List[str]:
        """Tenta extrair imports/requires (básico)."""
        imports = []
        if not self.content:
            return imports

        lines = self.content.splitlines()

        if self.language in ('javascript', 'js'):
            import re
            patterns = [
                r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]',
                r'require\s*\(\s*[\'"]([^\'"]+)[\'"]',
                r'import\s*\(\s*[\'"]([^\'"]+)[\'"]'
            ]
            for line in lines:
                for pattern in patterns:
                    matches = re.findall(pattern, line)
                    imports.extend(matches)

        elif self.language in ('python', 'py'):
            import re
            patterns = [
                r'import\s+(\w+)',
                r'from\s+(\w+)\s+import',
            ]
            for line in lines:
                for pattern in patterns:
                    matches = re.findall(pattern, line)
                    imports.extend(matches)

        return list(set(imports))  # Remove duplicatas

    @classmethod
    def create_javascript(cls, content: str, is_inline: bool = False, **kwargs) -> CodeObject:
        """Cria objeto de código JavaScript."""
        return cls(
            content=content,
            language='javascript',
            is_inline=is_inline,
            **kwargs
        )

    @classmethod
    def create_css(cls, content: str, **kwargs) -> CodeObject:
        """Cria objeto de código CSS (será StyleObject na verdade)."""
        return StyleObject(content=content, **kwargs)

    @classmethod
    def create_python(cls, content: str, **kwargs) -> CodeObject:
        """Cria objeto de código Python."""
        return cls(
            content=content,
            language='python',
            is_inline=False,
            **kwargs
        )


@dataclass
class StyleObject(ContentObject):
    """Objeto específico para CSS."""

    content: str = ""
    is_inline: bool = False  # style attribute vs <style> tag
    media: Optional[str] = None  # media queries
    source_file: Optional[str] = None

    object_type: str = ObjectType.STYLE

    def get_content(self) -> str:
        """Retorna representação textual do CSS."""
        if self.is_inline:
            return f"[INLINE-STYLE: {self.content[:50]}...]" if len(
                self.content) > 50 else f"[INLINE-STYLE: {self.content}]"
        else:
            media_label = f" ({self.media})" if self.media else ""
            return f"[CSS{media_label}]\n{self.content}\n[/CSS]"

    def get_raw_data(self) -> Dict[str, Any]:
        return {
            'content': self.content,
            'is_inline': self.is_inline,
            'media': self.media,
            'source_file': self.source_file,
            'rule_count': self.get_rule_count(),
            'char_count': len(self.content)
        }

    def get_rule_count(self) -> int:
        """Conta número aproximado de regras CSS."""
        if not self.content:
            return 0
        # Conta chaves de abertura como aproximação
        return self.content.count('{')

    def get_selectors(self) -> List[str]:
        """Extrai seletores CSS (básico)."""
        selectors = []
        if not self.content:
            return selectors

        import re
        # Padrão básico para pegar texto antes de {
        pattern = r'([^{}]+)\s*{'
        matches = re.findall(pattern, self.content)

        for match in matches:
            # Limpa e divide múltiplos seletores
            clean_selectors = [s.strip() for s in match.split(',')]
            selectors.extend(clean_selectors)

        # Remove vazios e comentários
        selectors = [s for s in selectors if s and not s.startswith('/*')]
        return selectors

    def get_properties(self) -> List[str]:
        """Extrai propriedades CSS únicas."""
        properties = []
        if not self.content:
            return properties

        import re
        # Padrão para propriedades CSS
        pattern = r'(\w+(?:-\w+)*)\s*:'
        matches = re.findall(pattern, self.content)

        return list(set(matches))  # Remove duplicatas

    def has_media_queries(self) -> bool:
        """Verifica se contém media queries."""
        return '@media' in self.content.lower()

    def get_media_queries(self) -> List[str]:
        """Extrai media queries."""
        if not self.has_media_queries():
            return []

        import re
        pattern = r'@media\s+([^{]+)'
        matches = re.findall(pattern, self.content, re.IGNORECASE)
        return [m.strip() for m in matches]

    def is_empty(self) -> bool:
        """Verifica se o CSS está vazio."""
        return not self.content.strip()

    @classmethod
    def create_inline(cls, content: str, **kwargs) -> StyleObject:
        """Cria objeto de CSS inline."""
        return cls(content=content, is_inline=True, **kwargs)

    @classmethod
    def create_block(cls, content: str, media: str = None, **kwargs) -> StyleObject:
        """Cria objeto de CSS em bloco."""
        return cls(content=content, is_inline=False, media=media, **kwargs)


@dataclass
class ScriptObject(CodeObject):
    """Objeto específico para JavaScript/scripts."""

    script_type: str = "javascript"  # javascript, json, etc.
    is_external: bool = False  # src vs inline
    src_url: Optional[str] = None  # URL do script externo
    defer: bool = False
    async_load: bool = False

    def __post_init__(self):
        super().__post_init__()
        self.language = self.script_type

    def get_content(self) -> str:
        """Retorna representação textual do script."""
        if self.is_external:
            return f"[SCRIPT: {self.src_url}]" if self.src_url else "[EXTERNAL-SCRIPT]"
        else:
            return super().get_content()

    def get_raw_data(self) -> Dict[str, Any]:
        data = super().get_raw_data()
        data.update({
            'script_type': self.script_type,
            'is_external': self.is_external,
            'src_url': self.src_url,
            'defer': self.defer,
            'async_load': self.async_load
        })
        return data

    def is_json(self) -> bool:
        """Verifica se é um script JSON."""
        return self.script_type.lower() in ('json', 'application/json')

    def parse_json(self) -> Any:
        """Tenta fazer parse do conteúdo como JSON."""
        if not self.is_json() or not self.content:
            return None

        try:
            import json
            return json.loads(self.content)
        except json.JSONDecodeError:
            return None

    def get_globals(self) -> List[str]:
        """Tenta extrair variáveis globais definidas."""
        globals_vars = []
        if not self.content or self.is_external:
            return globals_vars

        import re
        lines = self.content.splitlines()

        # Padrões para variáveis globais
        patterns = [
            r'var\s+(\w+)',
            r'let\s+(\w+)',
            r'const\s+(\w+)',
            r'window\.(\w+)',
            r'global\.(\w+)'
        ]

        for line in lines:
            for pattern in patterns:
                matches = re.findall(pattern, line)
                globals_vars.extend(matches)

        return list(set(globals_vars))  # Remove duplicatas

    def has_jquery(self) -> bool:
        """Verifica se usa jQuery."""
        if not self.content:
            return False
        return '$(' in self.content or 'jQuery(' in self.content

    def get_event_handlers(self) -> List[str]:
        """Extrai event handlers básicos."""
        handlers = []
        if not self.content:
            return handlers

        import re
        # Padrões comuns para eventos
        patterns = [
            r'addEventListener\([\'"](\w+)[\'"]',
            r'on(\w+)\s*=',
            r'\.on\([\'"](\w+)[\'"]',
            r'\.(\w+)\s*\(',  # métodos que podem ser eventos
        ]

        for pattern in patterns:
            matches = re.findall(pattern, self.content)
            handlers.extend(matches)

        # Filtra apenas eventos conhecidos
        known_events = {
            'click', 'load', 'ready', 'submit', 'change', 'keyup', 'keydown',
            'mouseenter', 'mouseleave', 'focus', 'blur', 'resize', 'scroll'
        }

        return [h for h in set(handlers) if h.lower() in known_events]

    @classmethod
    def create_external(cls, src_url: str, defer: bool = False, async_load: bool = False, **kwargs) -> ScriptObject:
        """Cria objeto para script externo."""
        return cls(
            content="",
            is_external=True,
            src_url=src_url,
            defer=defer,
            async_load=async_load,
            **kwargs
        )

    @classmethod
    def create_inline(cls, content: str, **kwargs) -> ScriptObject:
        """Cria objeto para script inline."""
        return cls(
            content=content,
            is_external=False,
            **kwargs
        )

    @classmethod
    def create_json(cls, json_content: str, **kwargs) -> ScriptObject:
        """Cria objeto para script JSON."""
        return cls(
            content=json_content,
            script_type='json',
            is_external=False,
            **kwargs
        )