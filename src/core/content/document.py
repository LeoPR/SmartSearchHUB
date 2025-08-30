# src/core/content/document.py - NOVO ARQUIVO
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
from .base import ContentObject, ObjectType


@dataclass
class PdfPageObject(ContentObject):
    """Objeto para página individual de PDF."""

    page_number: int = 1
    text_content: str = ""
    word_count: int = 0
    char_count: int = 0

    object_type: str = "pdf_page"

    def __post_init__(self):
        super().__post_init__()
        if not self.word_count and self.text_content:
            self.word_count = len(self.text_content.split())
        if not self.char_count and self.text_content:
            self.char_count = len(self.text_content)

    def get_content(self) -> str:
        """Retorna o texto da página."""
        return self.text_content

    def get_raw_data(self) -> Dict[str, Any]:
        return {
            'page_number': self.page_number,
            'text_content': self.text_content,
            'word_count': self.word_count,
            'char_count': self.char_count
        }

    def is_empty(self) -> bool:
        """Verifica se a página está vazia."""
        return not self.text_content.strip()

    def get_preview(self, length: int = 200) -> str:
        """Retorna preview do conteúdo da página."""
        text = self.text_content.strip()
        if len(text) <= length:
            return text
        return text[:length] + "..."

    def get_sentences(self) -> list:
        """Extrai sentenças da página."""
        import re
        # Split simples por pontuação
        sentences = re.split(r'[.!?]+', self.text_content)
        return [s.strip() for s in sentences if s.strip()]

    def search_text(self, query: str, case_sensitive: bool = False) -> list:
        """Busca texto na página."""
        import re
        
        text = self.text_content
        if not case_sensitive:
            text = text.lower()
            query = query.lower()

        matches = []
        for match in re.finditer(re.escape(query), text):
            start, end = match.span()
            context_start = max(0, start - 50)
            context_end = min(len(text), end + 50)
            
            matches.append({
                'start': start,
                'end': end,
                'context': text[context_start:context_end],
                'page_number': self.page_number
            })

        return matches


@dataclass
class PdfMetadataObject(ContentObject):
    """Objeto para metadados de PDF."""

    title: str = ""
    author: str = ""
    subject: str = ""
    pages_count: int = 0
    creation_date: str = ""
    modification_date: str = ""
    producer: str = ""
    pdf_version: str = ""
    encrypted: bool = False

    object_type: str = "pdf_metadata"

    def get_content(self) -> str:
        """Retorna representação textual dos metadados."""
        parts = []
        
        if self.title:
            parts.append(f"Título: {self.title}")
        if self.author:
            parts.append(f"Autor: {self.author}")
        if self.subject:
            parts.append(f"Assunto: {self.subject}")
        
        parts.append(f"Páginas: {self.pages_count}")
        
        if self.creation_date:
            parts.append(f"Criado: {self.creation_date}")
        if self.producer:
            parts.append(f"Produtor: {self.producer}")
        if self.encrypted:
            parts.append("PDF Criptografado: Sim")

        return "\n".join(parts)

    def get_raw_data(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'author': self.author,
            'subject': self.subject,
            'pages_count': self.pages_count,
            'creation_date': self.creation_date,
            'modification_date': self.modification_date,
            'producer': self.producer,
            'pdf_version': self.pdf_version,
            'encrypted': self.encrypted
        }

    def has_author(self) -> bool:
        """Verifica se tem autor definido."""
        return bool(self.author.strip())

    def has_title(self) -> bool:
        """Verifica se tem título definido."""
        return bool(self.title.strip())

    def is_encrypted(self) -> bool:
        """Verifica se o PDF está criptografado."""
        return self.encrypted

    def get_summary(self) -> str:
        """Retorna resumo dos metadados."""
        summary_parts = []
        
        if self.title:
            summary_parts.append(f'"{self.title}"')
        if self.author:
            summary_parts.append(f"por {self.author}")
        
        summary_parts.append(f"{self.pages_count} página(s)")
        
        if self.encrypted:
            summary_parts.append("(criptografado)")

        return " - ".join(summary_parts)


@dataclass
class PdfSectionObject(ContentObject):
    """Objeto para seção de PDF (baseado em estrutura de headings)."""

    section_title: str = ""
    section_level: int = 1
    page_start: int = 1
    page_end: int = 1
    content: str = ""

    object_type: str = "pdf_section"

    def get_content(self) -> str:
        """Retorna o conteúdo da seção."""
        if self.section_title:
            return f"[SEÇÃO: {self.section_title}]\n{self.content}"
        return self.content

    def get_raw_data(self) -> Dict[str, Any]:
        return {
            'section_title': self.section_title,
            'section_level': self.section_level,
            'page_start': self.page_start,
            'page_end': self.page_end,
            'content': self.content,
            'page_span': self.page_end - self.page_start + 1
        }

    def get_page_span(self) -> int:
        """Retorna quantas páginas a seção abrange."""
        return self.page_end - self.page_start + 1

    def is_single_page(self) -> bool:
        """Verifica se a seção está em uma única página."""
        return self.page_start == self.page_end