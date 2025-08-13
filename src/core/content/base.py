# src/core/content/base.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union
from abc import ABC, abstractmethod


@dataclass
class Position:
    """Localização do objeto no documento original."""
    start_line: Optional[int] = None
    start_col: Optional[int] = None
    end_line: Optional[int] = None
    end_col: Optional[int] = None
    xpath: Optional[str] = None  # Para HTML/XML
    element_id: Optional[str] = None
    element_class: Optional[str] = None


@dataclass
class ContentObject(ABC):
    """Classe base para todos os objetos de conteúdo extraído."""

    # Identificação
    object_type: str = field(init=False)  # Será definido pelas subclasses
    object_id: Optional[str] = None

    # Metadados
    metadata: Dict[str, Any] = field(default_factory=dict)
    position: Optional[Position] = None
    confidence: float = 1.0  # Confiança na extração (0.0 - 1.0)

    # Hierarquia
    parent: Optional[ContentObject] = field(default=None, repr=False)
    children: list[ContentObject] = field(default_factory=list, repr=False)

    def __post_init__(self):
        if not hasattr(self, 'object_type') or not self.object_type:
            self.object_type = self.__class__.__name__.lower().replace('object', '')

    @abstractmethod
    def get_content(self) -> str:
        """Retorna a representação textual do objeto."""
        pass

    @abstractmethod
    def get_raw_data(self) -> Any:
        """Retorna os dados brutos do objeto."""
        pass

    def add_child(self, child: ContentObject) -> None:
        """Adiciona um objeto filho."""
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: ContentObject) -> None:
        """Remove um objeto filho."""
        if child in self.children:
            child.parent = None
            self.children.remove(child)

    def get_ancestors(self) -> list[ContentObject]:
        """Retorna lista de objetos ancestrais."""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors

    def get_descendants(self, object_type: Optional[str] = None) -> list[ContentObject]:
        """Retorna todos os descendentes, opcionalmente filtrados por tipo."""
        descendants = []
        for child in self.children:
            if object_type is None or child.object_type == object_type:
                descendants.append(child)
            descendants.extend(child.get_descendants(object_type))
        return descendants

    def to_dict(self) -> Dict[str, Any]:
        """Serializa objeto para dicionário."""
        return {
            'object_type': self.object_type,
            'object_id': self.object_id,
            'content': self.get_content(),
            'metadata': self.metadata,
            'position': self.position.__dict__ if self.position else None,
            'confidence': self.confidence,
            'children_count': len(self.children)
        }

    def __str__(self) -> str:
        content = self.get_content()
        preview = content[:50] + '...' if len(content) > 50 else content
        return f"{self.object_type}('{preview}')"


@dataclass
class ContainerObject(ContentObject):
    """Objeto que pode conter outros objetos (base para listas, tabelas, etc)."""

    def get_content(self) -> str:
        """Concatena conteúdo de todos os filhos."""
        return '\n'.join(child.get_content() for child in self.children)

    def get_raw_data(self) -> list:
        """Retorna dados brutos de todos os filhos."""
        return [child.get_raw_data() for child in self.children]


# Enums para tipos comuns
class ObjectType:
    TEXT = "text"
    HEADING = "heading"
    URL = "url"
    LINK = "link"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TABLE = "table"
    LIST = "list"
    LIST_ITEM = "list_item"
    CODE = "code"
    STYLE = "style"
    CONTAINER = "container"