# examples/common/content_extractor.py
"""
ContentExtractor - Extração genérica de conteúdo para SmartSearchHUB.

Funcionalidades:
- Filtragem inteligente por tipo MIME e nome
- Extração de texto limpo de HTML/documentos
- Análise de links (internos vs externos)
- Estatísticas de conteúdo (palavras, linhas)
- Genérico: funciona com diferentes fontes de arquivo
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from urllib.parse import urlparse, urljoin


class ContentExtractor:
    """Extrator genérico de conteúdo de arquivos."""

    def __init__(self, 
                 extract_links: bool = True,
                 base_url: Optional[str] = None,
                 preview_length: int = 300):
        """
        Inicializa o extrator de conteúdo.

        Args:
            extract_links: Se deve extrair e analisar links
            base_url: URL base para resolver links relativos
            preview_length: Tamanho do preview de texto
        """
        self.extract_links = extract_links
        self.base_url = base_url
        self.preview_length = preview_length

    def is_extractable(self, file_obj: Any) -> bool:
        """
        Verifica se arquivo é adequado para extração de conteúdo.

        Args:
            file_obj: Objeto de arquivo (deve ter .name e .mimetype)

        Returns:
            True se arquivo é HTML, texto ou documento processável
        """
        name = getattr(file_obj, 'name', '').lower()
        mimetype = getattr(file_obj, 'mimetype', '').lower()

        # HTML explícito
        if mimetype.startswith('text/html') or name.endswith(('.html', '.htm')):
            return True

        # Google Docs (serão exportados como HTML)
        if mimetype.startswith('application/vnd.google-apps.document'):
            return True

        # Texto puro
        if mimetype.startswith('text/plain') or name.endswith(('.txt', '.md')):
            return True

        # Google Sheets (podem ser exportados como HTML)
        if mimetype.startswith('application/vnd.google-apps.spreadsheet'):
            return True

        return False

    def extract_content(self, file_obj: Any, **kwargs) -> Dict[str, Any]:
        """
        Extrai conteúdo estruturado de um arquivo.

        Args:
            file_obj: Objeto de arquivo (deve ter get_raw())
            **kwargs: Argumentos para get_raw() (head, permanent, etc.)

        Returns:
            Dict com dados extraídos:
            - raw_content: Conteúdo bruto
            - clean_text: Texto limpo
            - statistics: Estatísticas básicas
            - links: Links encontrados (se extract_links=True)
            - metadata: Metadados extras
        """
        # Obtém conteúdo bruto
        try:
            raw_content = file_obj.get_raw(**kwargs)
        except Exception as e:
            return {
                'error': f"Erro ao obter conteúdo: {e}",
                'raw_content': '',
                'clean_text': '',
                'statistics': {},
                'links': [],
                'metadata': {}
            }

        # Extrai texto limpo
        clean_text = self._extract_clean_text(raw_content, file_obj)

        # Calcula estatísticas
        statistics = self._calculate_statistics(raw_content, clean_text)

        # Extrai links se solicitado
        links = []
        if self.extract_links:
            links = self._extract_links(raw_content, file_obj)

        # Metadados do arquivo
        metadata = {
            'file_name': getattr(file_obj, 'name', ''),
            'file_mimetype': getattr(file_obj, 'mimetype', ''),
            'file_id': getattr(file_obj, 'id', ''),
            'content_type': self._detect_content_type(raw_content, file_obj)
        }

        return {
            'raw_content': raw_content,
            'clean_text': clean_text,
            'statistics': statistics,
            'links': links,
            'metadata': metadata,
            'preview': clean_text[:self.preview_length] if clean_text else ''
        }

    def _extract_clean_text(self, raw_content: str, file_obj: Any) -> str:
        """Extrai texto limpo do conteúdo bruto."""
        if not raw_content:
            return ''

        mimetype = getattr(file_obj, 'mimetype', '').lower()

        # HTML: remove tags e normaliza
        if mimetype.startswith(('text/html', 'application/vnd.google-apps')):
            return self._clean_html_text(raw_content)

        # Texto puro: apenas normaliza
        return self._normalize_text(raw_content)

    def _clean_html_text(self, html_content: str) -> str:
        """Remove tags HTML e extrai texto limpo."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            # Fallback simples sem BeautifulSoup
            return self._simple_html_clean(html_content)

        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove scripts e styles
        for script in soup(['script', 'style', 'noscript']):
            script.decompose()

        # Extrai texto
        text = soup.get_text(separator=' ')

        # Normaliza
        return self._normalize_text(text)

    def _simple_html_clean(self, html_content: str) -> str:
        """Limpeza simples de HTML sem bibliotecas externas."""
        # Remove tags HTML
        text = re.sub(r'<[^>]+>', ' ', html_content)
        
        # Remove entidades HTML comuns
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')

        return self._normalize_text(text)

    def _normalize_text(self, text: str) -> str:
        """Normaliza texto: espaços, quebras de linha, etc."""
        # Remove espaços extras
        text = re.sub(r'\s+', ' ', text)
        
        # Remove linhas muito curtas (provavelmente navegação/menu)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) > 20:  # Só linhas com conteúdo substancial
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines).strip()

    def _extract_links(self, content: str, file_obj: Any) -> List[Dict[str, Any]]:
        """Extrai e analisa links do conteúdo."""
        links = []
        mimetype = getattr(file_obj, 'mimetype', '').lower()

        if mimetype.startswith(('text/html', 'application/vnd.google-apps')):
            links.extend(self._extract_html_links(content))
        
        # Adiciona links de texto puro (URLs simples)
        links.extend(self._extract_text_links(content))

        # Classifica links
        for link in links:
            link.update(self._classify_link(link['url']))

        return links

    def _extract_html_links(self, html_content: str) -> List[Dict[str, Any]]:
        """Extrai links de HTML usando BeautifulSoup ou regex."""
        links = []

        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag.get('href', '').strip()
                text = a_tag.get_text(strip=True)
                
                if href:
                    links.append({
                        'url': href,
                        'text': text,
                        'title': a_tag.get('title', ''),
                        'type': 'html_link'
                    })
        except ImportError:
            # Fallback com regex
            link_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
            matches = re.findall(link_pattern, html_content, re.IGNORECASE | re.DOTALL)
            
            for url, text in matches:
                # Remove tags do texto
                text = re.sub(r'<[^>]+>', '', text).strip()
                
                links.append({
                    'url': url,
                    'text': text,
                    'title': '',
                    'type': 'html_link'
                })

        return links

    def _extract_text_links(self, content: str) -> List[Dict[str, Any]]:
        """Extrai URLs simples do texto."""
        links = []
        
        # Regex para URLs
        url_pattern = r'https?://[^\s<>"\'{}|\\^`\[\]]+'
        matches = re.findall(url_pattern, content)
        
        for url in matches:
            links.append({
                'url': url,
                'text': url,
                'title': '',
                'type': 'text_url'
            })

        return links

    def _classify_link(self, url: str) -> Dict[str, Any]:
        """Classifica um link como interno/externo/etc."""
        classification = {
            'is_internal': False,
            'is_external': False,
            'is_anchor': False,
            'domain': '',
            'resolved_url': url
        }

        # Link de âncora
        if url.startswith('#'):
            classification['is_anchor'] = True
            return classification

        # URL relativa ou absoluta
        try:
            parsed = urlparse(url)
            
            if parsed.scheme and parsed.netloc:
                # URL absoluta
                classification['is_external'] = True
                classification['domain'] = parsed.netloc
            else:
                # URL relativa
                classification['is_internal'] = True
                
                # Resolve URL relativa se temos base_url
                if self.base_url:
                    classification['resolved_url'] = urljoin(self.base_url, url)
                    resolved_parsed = urlparse(classification['resolved_url'])
                    classification['domain'] = resolved_parsed.netloc

        except Exception:
            pass  # Mantém valores padrão

        return classification

    def _calculate_statistics(self, raw_content: str, clean_text: str) -> Dict[str, Any]:
        """Calcula estatísticas básicas do conteúdo."""
        stats = {
            'raw_length': len(raw_content),
            'clean_length': len(clean_text),
            'raw_lines': len(raw_content.splitlines()) if raw_content else 0,
            'clean_lines': len(clean_text.splitlines()) if clean_text else 0,
            'word_count': 0,
            'paragraph_count': 0,
            'compression_ratio': 0.0
        }

        if clean_text:
            # Contagem de palavras
            words = re.findall(r'\b\w+\b', clean_text)
            stats['word_count'] = len(words)

            # Contagem de parágrafos (linhas não vazias)
            paragraphs = [p.strip() for p in clean_text.split('\n') if p.strip()]
            stats['paragraph_count'] = len(paragraphs)

        # Taxa de compressão (HTML → texto limpo)
        if stats['raw_length'] > 0:
            stats['compression_ratio'] = stats['clean_length'] / stats['raw_length']

        return stats

    def _detect_content_type(self, raw_content: str, file_obj: Any) -> str:
        """Detecta tipo de conteúdo mais específico."""
        mimetype = getattr(file_obj, 'mimetype', '').lower()
        name = getattr(file_obj, 'name', '').lower()

        # Google Apps
        if mimetype.startswith('application/vnd.google-apps.document'):
            return 'google_document'
        elif mimetype.startswith('application/vnd.google-apps.spreadsheet'):
            return 'google_spreadsheet'
        elif mimetype.startswith('application/vnd.google-apps.presentation'):
            return 'google_presentation'

        # HTML
        if mimetype.startswith('text/html') or name.endswith(('.html', '.htm')):
            # Tenta detectar se é uma página completa ou fragmento
            if '<html' in raw_content.lower() and '<body' in raw_content.lower():
                return 'html_page'
            else:
                return 'html_fragment'

        # Texto
        if mimetype.startswith('text/plain') or name.endswith('.txt'):
            return 'plain_text'

        # Markdown
        if name.endswith('.md'):
            return 'markdown'

        return 'unknown'

    def filter_extractable_files(self, files: List[Any]) -> List[Any]:
        """
        Filtra lista de arquivos, retornando apenas os processáveis.

        Args:
            files: Lista de objetos de arquivo

        Returns:
            Lista filtrada de arquivos processáveis
        """
        return [f for f in files if self.is_extractable(f)]

    def batch_extract(self, files: List[Any], **kwargs) -> List[Dict[str, Any]]:
        """
        Processa múltiplos arquivos em lote.

        Args:
            files: Lista de arquivos a processar
            **kwargs: Argumentos para extract_content()

        Returns:
            Lista de resultados da extração
        """
        results = []
        
        for file_obj in files:
            if self.is_extractable(file_obj):
                result = self.extract_content(file_obj, **kwargs)
                result['file_metadata'] = {
                    'name': getattr(file_obj, 'name', ''),
                    'mimetype': getattr(file_obj, 'mimetype', ''),
                    'id': getattr(file_obj, 'id', '')
                }
                results.append(result)

        return results

    # examples/common/content_extractor.py - ATUALIZAÇÃO PARA PDF
    # Adicionar estas linhas na classe ContentExtractor:

    def is_extractable(self, file_obj: Any) -> bool:
        """
        Verifica se arquivo é adequado para extração de conteúdo.
        ATUALIZADO: Agora inclui suporte a PDF.
        """
        name = getattr(file_obj, 'name', '').lower()
        mimetype = getattr(file_obj, 'mimetype', '').lower()

        # HTML explícito
        if mimetype.startswith('text/html') or name.endswith(('.html', '.htm')):
            return True

        # Google Docs (serão exportados como HTML)
        if mimetype.startswith('application/vnd.google-apps.document'):
            return True

        # Texto puro
        if mimetype.startswith('text/plain') or name.endswith(('.txt', '.md')):
            return True

        # Google Sheets (podem ser exportados como HTML)
        if mimetype.startswith('application/vnd.google-apps.spreadsheet'):
            return True

        # PDF - NOVO SUPORTE
        if mimetype.startswith('application/pdf') or name.endswith('.pdf'):
            return True

        return False

    def extract_content(self, file_obj: Any, **kwargs) -> Dict[str, Any]:
        """
        Extrai conteúdo estruturado de um arquivo.
        ATUALIZADO: Agora suporta PDF além de HTML.
        """
        # Obtém conteúdo bruto
        try:
            # Detecta tipo de arquivo
            file_type = self._detect_content_type('', file_obj)

            if file_type.startswith('pdf'):
                return self._extract_pdf_content(file_obj, **kwargs)
            else:
                # Lógica existente para HTML/texto
                raw_content = file_obj.get_raw(**kwargs)
        except Exception as e:
            return {
                'error': f"Erro ao obter conteúdo: {e}",
                'raw_content': '',
                'clean_text': '',
                'statistics': {},
                'links': [],
                'metadata': {},
                'content_type': 'unknown'
            }

        # Resto da lógica existente para HTML/texto...
        clean_text = self._extract_clean_text(raw_content, file_obj)
        statistics = self._calculate_statistics(raw_content, clean_text)

        # Links só para HTML
        links = []
        if self.extract_links and not file_type.startswith('pdf'):
            links = self._extract_links(raw_content, file_obj)

        metadata = {
            'file_name': getattr(file_obj, 'name', ''),
            'file_mimetype': getattr(file_obj, 'mimetype', ''),
            'file_id': getattr(file_obj, 'id', ''),
            'content_type': file_type
        }

        return {
            'raw_content': raw_content,
            'clean_text': clean_text,
            'statistics': statistics,
            'links': links,
            'metadata': metadata,
            'preview': clean_text[:self.preview_length] if clean_text else ''
        }

    def _extract_pdf_content(self, file_obj: Any, **kwargs) -> Dict[str, Any]:
        """Extrai conteúdo estruturado de PDF."""
        try:
            # Verifica se o objeto tem métodos específicos de PDF
            if hasattr(file_obj, 'get_metadata') and hasattr(file_obj, 'get_text'):
                # Usa métodos específicos do PDF wrapper
                metadata = file_obj.get_metadata()

                # Configurações específicas para PDF
                max_pages = kwargs.get('max_pages', 5)
                text = file_obj.get_text(max_pages=max_pages, include_page_breaks=True)

                # Informações de páginas se disponível
                pages_info = []
                if hasattr(file_obj, 'get_pages'):
                    try:
                        pages_data = file_obj.get_pages(max_pages=max_pages)
                        pages_info = [
                            {
                                'page_number': p.get('page_number', i + 1),
                                'word_count': p.get('word_count', 0),
                                'char_count': p.get('char_count', 0)
                            }
                            for i, p in enumerate(pages_data)
                        ]
                    except Exception:
                        pass

                # Estatísticas específicas de PDF
                statistics = self._calculate_pdf_statistics(text, metadata, pages_info)

            else:
                # Fallback para método genérico
                raw_content = file_obj.get_raw(**kwargs)
                text = self._extract_clean_text(raw_content, file_obj)
                statistics = self._calculate_statistics(raw_content, text)
                metadata = {}
                pages_info = []

            return {
                'raw_content': text,  # Para PDF, texto já é "limpo"
                'clean_text': text,
                'statistics': statistics,
                'links': [],  # PDFs não têm links como HTML
                'metadata': {
                    'file_name': getattr(file_obj, 'name', ''),
                    'file_mimetype': getattr(file_obj, 'mimetype', ''),
                    'file_id': getattr(file_obj, 'id', ''),
                    'content_type': 'pdf',
                    'pdf_metadata': metadata,
                    'pages_info': pages_info
                },
                'preview': text[:self.preview_length] if text else '',
                'content_type': 'pdf'
            }

        except Exception as e:
            return {
                'error': f"Erro na extração PDF: {e}",
                'raw_content': '',
                'clean_text': '',
                'statistics': {},
                'links': [],
                'metadata': {'content_type': 'pdf'},
                'content_type': 'pdf'
            }

    def _calculate_pdf_statistics(self, text: str, pdf_metadata: Dict, pages_info: List) -> Dict[str, Any]:
        """Calcula estatísticas específicas para PDF."""
        stats = self._calculate_statistics(text, text)  # Usa método base

        # Adiciona estatísticas específicas de PDF
        stats.update({
            'pdf_pages': pdf_metadata.get('pages_count', len(pages_info)),
            'pdf_title': pdf_metadata.get('title', ''),
            'pdf_author': pdf_metadata.get('author', ''),
            'pdf_type': pdf_metadata.get('pdf_type', 'unknown'),
            'extraction_method': pdf_metadata.get('extraction_method', 'unknown'),
            'encrypted': pdf_metadata.get('encrypted', False),
            'pages_processed': len(pages_info)
        })

        # Estatísticas por página se disponível
        if pages_info:
            total_page_words = sum(p.get('word_count', 0) for p in pages_info)
            stats['avg_words_per_page'] = total_page_words / len(pages_info) if pages_info else 0
            stats['pages_with_text'] = len([p for p in pages_info if p.get('word_count', 0) > 0])

        return stats

    def _detect_content_type(self, raw_content: str, file_obj: Any) -> str:
        """
        Detecta tipo de conteúdo mais específico.
        ATUALIZADO: Inclui detecção de PDF.
        """
        mimetype = getattr(file_obj, 'mimetype', '').lower()
        name = getattr(file_obj, 'name', '').lower()

        # PDF
        if mimetype.startswith('application/pdf') or name.endswith('.pdf'):
            return 'pdf_document'

        # Google Apps
        if mimetype.startswith('application/vnd.google-apps.document'):
            return 'google_document'
        elif mimetype.startswith('application/vnd.google-apps.spreadsheet'):
            return 'google_spreadsheet'
        elif mimetype.startswith('application/vnd.google-apps.presentation'):
            return 'google_presentation'

        # HTML
        if mimetype.startswith('text/html') or name.endswith(('.html', '.htm')):
            if '<html' in raw_content.lower() and '<body' in raw_content.lower():
                return 'html_page'
            else:
                return 'html_fragment'

        # Texto
        if mimetype.startswith('text/plain') or name.endswith('.txt'):
            return 'plain_text'

        # Markdown
        if name.endswith('.md'):
            return 'markdown'

        return 'unknown'

    def filter_extractable_files(self, files: List[Any]) -> List[Any]:
        """
        Filtra lista de arquivos, retornando apenas os processáveis.
        ATUALIZADO: Agora inclui PDFs.
        """
        return [f for f in files if self.is_extractable(f)]

    # Método auxiliar para filtrar apenas PDFs
    def filter_pdf_files(self, files: List[Any]) -> List[Any]:
        """Filtra apenas arquivos PDF."""
        pdf_files = []
        for file_obj in files:
            name = getattr(file_obj, 'name', '').lower()
            mimetype = getattr(file_obj, 'mimetype', '').lower()

            if mimetype.startswith('application/pdf') or name.endswith('.pdf'):
                pdf_files.append(file_obj)

        return pdf_files


def quick_test():
    """Teste rápido do ContentExtractor."""
    print("🧪 Teste rápido do ContentExtractor...")

    # Simula objeto de arquivo
    class MockFile:
        def __init__(self, name, mimetype, content):
            self.name = name
            self.mimetype = mimetype
            self._content = content

        def get_raw(self, **kwargs):
            return self._content

    # Teste com HTML
    html_file = MockFile(
        "test.html",
        "text/html",
        "<html><body><h1>Título</h1><p>Conteúdo com <a href='https://example.com'>link</a>.</p></body></html>"
    )

    extractor = ContentExtractor(extract_links=True)

    print(f"📄 Arquivo processável: {extractor.is_extractable(html_file)}")

    result = extractor.extract_content(html_file)

    print(f"📊 Estatísticas:")
    for key, value in result['statistics'].items():
        print(f"   {key}: {value}")

    print(f"🔗 Links encontrados: {len(result['links'])}")
    for link in result['links']:
        print(f"   - {link['text']}: {link['url']}")

    print(f"📝 Preview: {result['preview'][:100]}...")

    return True


if __name__ == "__main__":
    quick_test()