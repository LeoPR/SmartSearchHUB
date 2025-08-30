# src/core/io/pdf.py - VERSÃO EXPANDIDA
from __future__ import annotations
from typing import List, Dict, Any, Optional, Union
from .baseobj import FileObject
import os
import tempfile
import base64
import traceback

# Imports dos content objects
from ..content.text import TextObject, HeadingObject
from ..content.base import ContentObject, Position
from ..content.document import PdfPageObject, PdfMetadataObject


class PdfAnalyzer:
    """Analisador avançado de PDFs."""

    def __init__(self):
        self.library_available = self._check_libraries()

    def _check_libraries(self) -> str:
        """Detecta biblioteca PDF disponível."""
        try:
            import fitz  # PyMuPDF
            return 'pymupdf'
        except ImportError:
            try:
                import pdfplumber
                return 'pdfplumber'
            except ImportError:
                try:
                    import PyPDF2
                    return 'pypdf2'
                except ImportError:
                    return 'none'

    def detect_pdf_type(self, content: bytes) -> str:
        """Detecta tipo de PDF: text-based, image-based, mixed."""
        if self.library_available == 'none':
            return 'unknown'

        try:
            if self.library_available == 'pymupdf':
                import fitz
                doc = fitz.open(stream=content, filetype="pdf")

                if len(doc) == 0:
                    return 'empty'

                # Analisa primeira página
                page = doc[0]
                text_blocks = page.get_text_blocks()
                images = page.get_images()

                has_text = len([b for b in text_blocks if b[4].strip()]) > 0
                has_images = len(images) > 0

                if has_text and has_images:
                    return 'mixed'
                elif has_text:
                    return 'text_based'
                elif has_images:
                    return 'image_based'
                else:
                    return 'empty'

        except Exception:
            pass

        return 'unknown'

    def get_metadata(self, content: bytes) -> Dict[str, Any]:
        """Extrai metadados do PDF."""
        metadata = {
            'title': '',
            'author': '',
            'subject': '',
            'pages_count': 0,
            'creation_date': '',
            'modification_date': '',
            'producer': '',
            'pdf_version': '',
            'encrypted': False,
            'extraction_method': self.library_available
        }

        if self.library_available == 'none':
            return metadata

        try:
            if self.library_available == 'pymupdf':
                import fitz
                doc = fitz.open(stream=content, filetype="pdf")

                # Metadados básicos
                meta = doc.metadata
                metadata.update({
                    'title': meta.get('title', ''),
                    'author': meta.get('author', ''),
                    'subject': meta.get('subject', ''),
                    'pages_count': len(doc),
                    'creation_date': meta.get('creationDate', ''),
                    'modification_date': meta.get('modDate', ''),
                    'producer': meta.get('producer', ''),
                    'encrypted': doc.needs_pass
                })

        except Exception:
            pass

        return metadata

    def extract_text_with_positions(self, content: bytes, max_pages: int = None) -> List[Dict]:
        """Extrai texto com informações de posição, com fallback para abrir via arquivo temporário e outros backends."""
        pages_data = []

        if self.library_available == 'none':
            return pages_data

        doc = None
        try:
            if self.library_available == 'pymupdf':
                import fitz

                # tentativa 1: abrir como stream
                try:
                    doc = fitz.open(stream=content, filetype="pdf")
                except Exception as e_stream:
                    if os.getenv("DEBUG"):
                        print(f"[DEBUG] fitz.open(stream) falhou: {e_stream}")
                        traceback.print_exc()
                    # tentativa 2: abrir via arquivo temporário (fallback)
                    try:
                        tf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                        try:
                            tf.write(content)
                            tf.flush()
                            tf.close()
                            doc = fitz.open(tf.name)
                            if os.getenv("DEBUG"):
                                print(f"[DEBUG] fitz.open via arquivo temporário funcionou ({tf.name})")
                        finally:
                            try:
                                os.unlink(tf.name)
                            except Exception:
                                pass
                    except Exception as e_file:
                        if os.getenv("DEBUG"):
                            print(f"[DEBUG] fitz.open(file) também falhou: {e_file}")
                            traceback.print_exc()
                        doc = None

                if doc is None:
                    # último recurso: tentar pdfplumber (se disponível)
                    try:
                        import pdfplumber, io as _io
                        with pdfplumber.open(_io.BytesIO(content)) as pdfpl:
                            total_pages = min(len(pdfpl.pages), max_pages or len(pdfpl.pages))
                            for page_num in range(total_pages):
                                p = pdfpl.pages[page_num]
                                text = p.extract_text() or ""
                                pages_data.append({
                                    'page_number': page_num + 1,
                                    'text': text,
                                    'word_count': len(text.split()),
                                    'char_count': len(text),
                                    'blocks_count': 0,
                                    'blocks': []
                                })
                            return pages_data
                    except Exception:
                        if os.getenv("DEBUG"):
                            print("[DEBUG] pdfplumber fallback falhou ou não instalado.")

                # se abrimos com fitz, extrair normalmente
                if doc:
                    total_pages = min(len(doc), max_pages or len(doc))
                    for page_num in range(total_pages):
                        page = doc[page_num]
                        text = page.get_text() or ""
                        blocks = page.get_text("blocks") or []
                        page_data = {
                            'page_number': page_num + 1,
                            'text': text,
                            'word_count': len(text.split()) if text else 0,
                            'char_count': len(text),
                            'blocks_count': len(blocks),
                            'blocks': [
                                {
                                    'text': block[4] if len(block) > 4 else '',
                                    'bbox': block[:4] if len(block) >= 4 else None
                                }
                                for block in blocks
                                if len(block) > 4 and block[4].strip()
                            ]
                        }
                        pages_data.append(page_data)

        except Exception:
            if os.getenv("DEBUG"):
                traceback.print_exc()
        finally:
            try:
                if doc:
                    doc.close()
            except Exception:
                pass

        return pages_data


class Pdf(FileObject):
    """Wrapper avançado para arquivos PDF seguindo padrão do framework."""

    def __init__(self, base_file):
        super().__init__(base_file)
        self._analyzer = PdfAnalyzer()
        self._cached_content = None
        self._cached_metadata = None

    def get_type(self) -> str:
        return "pdf"

    def get_pdf_content(self, use_cache: bool = True) -> bytes:
        """Obtém conteúdo binário do PDF (bytes, sem perda)."""
        if use_cache and self._cached_content is not None:
            return self._cached_content

        # Lê binário diretamente do cache
        try:
            content = self._f.get_bytes(permanent=False)
        except AttributeError:
            # Compatibilidade: se a interface ainda não tiver get_bytes, tenta ler do caminho diretamente
            # Atenção: esse bloco é apenas defensivo e pode ser removido quando get_bytes estiver garantido.
            path = self._f._ensure_local(permanent=False)  # uso interno para fallback
            content = path.read_bytes()

        if os.getenv("DEBUG"):
            try:
                print(f"[DEBUG] PDF bytes len: {len(content)} header: {content[:32]!r} startswith %PDF? {content.startswith(b'%PDF')}")
            except Exception:
                pass

        if use_cache:
            self._cached_content = content

        return content

    def get_metadata(self, use_cache: bool = True) -> Dict[str, Any]:
        """Obtém metadados do PDF."""
        if use_cache and self._cached_metadata is not None:
            return self._cached_metadata

        content = self.get_pdf_content(use_cache)
        metadata = self._analyzer.get_metadata(content)

        # Adiciona metadados do arquivo base
        metadata.update({
            'file_name': self.name,
            'file_id': self.id,
            'file_mimetype': self.mimetype,
            'pdf_type': self._analyzer.detect_pdf_type(content)
        })

        if use_cache:
            self._cached_metadata = metadata

        return metadata

    def get_text(self,
                 head=None,
                 permanent: bool = False,
                 max_pages: int = None,
                 include_page_breaks: bool = True,
                 **config) -> str:
        """
        Extrai texto do PDF.

        Args:
            head: Limitação de linhas/caracteres
            permanent: Se deve salvar permanentemente
            max_pages: Máximo de páginas a processar
            include_page_breaks: Se deve incluir quebras entre páginas
            **config: Configurações adicionais
        """
        content = self.get_pdf_content()
        pages_data = self._analyzer.extract_text_with_positions(
            content, max_pages=max_pages
        )

        if not pages_data:
            return ""

        # Combina texto das páginas
        text_parts = []
        for page_data in pages_data:
            page_text = page_data['text']
            if page_text.strip():
                if include_page_breaks and len(text_parts) > 0:
                    text_parts.append(f"\n--- Página {page_data['page_number']} ---\n")
                text_parts.append(page_text.strip())

        full_text = '\n'.join(text_parts)

        # Aplica limitação de head se especificada
        if head is not None:
            full_text = self._apply_head_limit(full_text, head)

        return full_text

    def get_pages(self, max_pages: int = None) -> List[Dict[str, Any]]:
        """Retorna informações detalhadas das páginas."""
        content = self.get_pdf_content()
        return self._analyzer.extract_text_with_positions(content, max_pages)

    def get_objects(self,
                    types: Optional[List[str]] = None,
                    max_pages: int = None,
                    **config) -> List[ContentObject]:
        """
        Extrai objetos estruturados do PDF (seguindo padrão HTML).

        Args:
            types: Lista de tipos a extrair (['text', 'metadata', 'page'])
            max_pages: Máximo de páginas a processar
            **config: Configurações adicionais
        """
        objects = []

        # Metadados do PDF
        if not types or 'metadata' in types:
            metadata = self.get_metadata()
            metadata_obj = PdfMetadataObject(
                title=metadata.get('title', ''),
                author=metadata.get('author', ''),
                pages_count=metadata.get('pages_count', 0),
                position=Position(),
                metadata=metadata
            )
            objects.append(metadata_obj)

        # Páginas individuais
        if not types or 'page' in types or 'text' in types:
            pages_data = self.get_pages(max_pages)

            for page_data in pages_data:
                # Objeto da página
                page_obj = PdfPageObject(
                    page_number=page_data['page_number'],
                    text_content=page_data['text'],
                    position=Position(),
                    metadata={
                        'word_count': page_data['word_count'],
                        'char_count': page_data['char_count'],
                        'blocks_count': page_data['blocks_count']
                    }
                )
                objects.append(page_obj)

                # Texto da página como TextObject
                if page_data['text'].strip():
                    text_obj = TextObject(
                        content=page_data['text'],
                        metadata={
                            'page_number': page_data['page_number'],
                            'source': 'pdf_page'
                        }
                    )
                    objects.append(text_obj)

        # Filtra por tipos se especificado
        if types:
            filtered_objects = []
            for obj in objects:
                if obj.object_type in types:
                    filtered_objects.append(obj)
            return filtered_objects

        return objects

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do PDF."""
        metadata = self.get_metadata()
        pages_data = self.get_pages()

        total_words = sum(page.get('word_count', 0) for page in pages_data)
        total_chars = sum(page.get('char_count', 0) for page in pages_data)

        return {
            'pages_count': len(pages_data),
            'total_words': total_words,
            'total_chars': total_chars,
            'avg_words_per_page': total_words / len(pages_data) if pages_data else 0,
            'pdf_type': metadata.get('pdf_type', 'unknown'),
            'extraction_method': metadata.get('extraction_method', 'unknown'),
            'has_text': total_chars > 0,
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'encrypted': metadata.get('encrypted', False)
        }

    def _apply_head_limit(self, text: str, head) -> str:
        """Aplica limitação de head ao texto (mesmo padrão HTML)."""
        if isinstance(head, int):
            return "\n".join(text.splitlines()[:head])

        if isinstance(head, dict):
            lines = head.get("lines")
            chars = head.get("characters")

            if lines is None and chars is None:
                return text

            if lines is not None:
                parts = text.splitlines()[: max(0, int(lines))]
                if chars is not None:
                    m = max(0, int(chars))
                    parts = [p[:m] for p in parts]
                return "\n".join(parts)

            if chars is not None:
                return text[: max(0, int(chars))]

        return text

    def is_text_extractable(self) -> bool:
        """Verifica se o PDF permite extração de texto."""
        try:
            content = self.get_pdf_content()
            pdf_type = self._analyzer.detect_pdf_type(content)
            return pdf_type in ['text_based', 'mixed']
        except:
            return False

    def clear_cache(self):
        """Limpa cache do PDF."""
        self._cached_content = None
        self._cached_metadata = None