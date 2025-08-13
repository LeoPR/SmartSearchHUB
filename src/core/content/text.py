# src/core/content/text.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .base import ContentObject, ObjectType


@dataclass
class TextObject(ContentObject):
    """Objeto para texto puro."""

    content: str = ""
    language: Optional[str] = None  # Idioma detectado
    formatting: Optional[dict] = None  # bold, italic, etc.

    object_type: str = ObjectType.TEXT

    def get_content(self) -> str:
        return self.content

    def get_raw_data(self) -> str:
        return self.content

    def is_empty(self) -> bool:
        return not self.content.strip()

    def word_count(self) -> int:
        return len(self.content.split())

    def char_count(self) -> int:
        return len(self.content)


@dataclass
class HeadingObject(ContentObject):
    """Objeto para cabeçalhos (h1, h2, etc)."""

    content: str = ""
    level: int = 1  # 1-6 para h1-h6
    anchor_id: Optional[str] = None

    object_type: str = ObjectType.HEADING

    def get_content(self) -> str:
        return self.content

    def get_raw_data(self) -> dict:
        return {
            'content': self.content,
            'level': self.level,
            'anchor_id': self.anchor_id
        }

    def to_markdown(self) -> str:
        """Converte para formato markdown."""
        prefix = '#' * self.level
        return f"{prefix} {self.content}"

    def is_top_level(self) -> bool:
        return self.level <= 2