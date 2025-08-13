# src/core/io/html.py - VERSÃO ATUALIZADA
from __future__ import annotations
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin, urlparse
from .baseobj import FileObject

# Imports dos content objects
from ..content.text import TextObject, HeadingObject
from ..content.link import UrlObject, LinkObject
from ..content.media import ImageObject, VideoObject, AudioObject
from ..content.structure import TableObject, ListObject, ListItemObject, SectionObject
from ..content.code import CodeObject, StyleObject, ScriptObject
from ..content.base import ContentObject, Position


class HtmlObjectParser:
    """Parser que converte HTML em objetos estruturados."""

    def __init__(self,
                 base_url: Optional[str] = None,
                 extract_scripts: bool = True,
                 extract_styles: bool = True,
                 extract_images: bool = True,
                 extract_links: bool = True,
                 resolve_relative_urls: bool = True):
        self.base_url = base_url
        self.extract_scripts = extract_scripts
        self.extract_styles = extract_styles
        self.extract_images = extract_images
        self.extract_links = extract_links
        self.resolve_relative_urls = resolve_relative_urls

        # Elementos que devem ser removidos
        self.skip_tags = {'script', 'style', 'noscript', 'iframe', 'embed', 'object'}

        # Para tracking de posição no documento
        self._element_counter = 0

    def parse(self, html_content: str) -> List[ContentObject]:
        """Converte HTML em lista de objetos estruturados."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Primeiro extrai scripts e styles se solicitado
        extracted_objects = []

        if self.extract_scripts:
            extracted_objects.extend(self._extract_scripts(soup))

        if self.extract_styles:
            extracted_objects.extend(self._extract_styles(soup))

        # Remove elementos que não queremos processar no conteúdo principal
        self._remove_processed_elements(soup)

        # Processa o body ou documento inteiro
        content_objects = []
        if soup.body:
            content_objects = self._process_element(soup.body)
        else:
            content_objects = self._process_element(soup)

        # Combina objetos extraídos + conteúdo
        return extracted_objects + content_objects

    def _extract_scripts(self, soup: BeautifulSoup) -> List[ScriptObject]:
        """Extrai todos os scripts do HTML."""
        scripts = []

        for script_tag in soup.find_all('script'):
            position = self._create_position(script_tag)

            # Script externo
            if script_tag.get('src'):
                src_url = script_tag['src']
                if self.resolve_relative_urls and self.base_url:
                    src_url = urljoin(self.base_url, src_url)

                script_obj = ScriptObject.create_external(
                    src_url=src_url,
                    defer=script_tag.get('defer', False),
                    async_load=script_tag.get('async', False),
                    position=position
                )

                # Adiciona metadados do tipo
                script_type = script_tag.get('type', 'text/javascript')
                script_obj.script_type = self._normalize_script_type(script_type)

            else:
                # Script inline
                content = script_tag.string or ""
                script_type = script_tag.get('type', 'text/javascript')

                script_obj = ScriptObject.create_inline(
                    content=content,
                    position=position
                )
                script_obj.script_type = self._normalize_script_type(script_type)

            scripts.append(script_obj)

        return scripts

    def _extract_styles(self, soup: BeautifulSoup) -> List[StyleObject]:
        """Extrai todos os estilos CSS do HTML."""
        styles = []

        # CSS em tags <style>
        for style_tag in soup.find_all('style'):
            position = self._create_position(style_tag)
            content = style_tag.string or ""
            media = style_tag.get('media')

            style_obj = StyleObject.create_block(
                content=content,
                media=media,
                position=position
            )
            styles.append(style_obj)

        # CSS inline em atributos style
        for element in soup.find_all(attrs={'style': True}):
            position = self._create_position(element)
            inline_css = element['style']

            if inline_css.strip():
                style_obj = StyleObject.create_inline(
                    content=inline_css,
                    position=position
                )
                # Adiciona contexto do elemento
                style_obj.metadata['element_tag'] = element.name
                style_obj.metadata['element_id'] = element.get('id')
                style_obj.metadata['element_class'] = element.get('class')

                styles.append(style_obj)

        return styles

    def _process_element(self, element, level: int = 0) -> List[ContentObject]:
        """Processa um elemento HTML recursivamente."""
        if isinstance(element, NavigableString):
            text = str(element).strip()
            if text:
                return [TextObject(content=text)]
            return []

        if not isinstance(element, Tag):
            return []

        tag_name = element.name.lower()
        position = self._create_position(element)

        # Dispatch para processadores específicos
        if tag_name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            return self._process_heading(element, position)
        elif tag_name == 'p':
            return self._process_paragraph(element, position, level)
        elif tag_name == 'a':
            return self._process_link(element, position)
        elif tag_name == 'img':
            return self._process_image(element, position)
        elif tag_name in ('video', 'audio'):
            return self._process_media(element, position)
        elif tag_name == 'table':
            return self._process_table(element, position)
        elif tag_name in ('ul', 'ol'):
            return self._process_list(element, position)
        elif tag_name == 'li':
            return self._process_list_item(element, position, level)
        elif tag_name in ('div', 'section', 'article', 'header', 'footer', 'main', 'aside'):
            return self._process_container(element, position, level)
        elif tag_name == 'br':
            return [TextObject(content='\n')]
        elif tag_name == 'hr':
            return [TextObject(content='\n' + '─' * 50 + '\n')]
        else:
            return self._process_generic(element, position, level)

    def _process_heading(self, element: Tag, position: Position) -> List[HeadingObject]:
        """Processa cabeçalhos (h1-h6)."""
        level = int(element.name[1])  # h1 -> 1, h2 -> 2, etc.
        text = element.get_text(strip=True)

        if not text:
            return []

        heading = HeadingObject(
            content=text,
            level=level,
            anchor_id=element.get('id'),
            position=position
        )

        return [heading]

    def _process_paragraph(self, element: Tag, position: Position, level: int) -> List[ContentObject]:
        """Processa parágrafos, pode conter texto + links + imagens."""
        objects = []

        for child in element.children:
            objects.extend(self._process_element(child, level + 1))

        # Se só tem texto, cria um TextObject único
        if len(objects) == 1 and isinstance(objects[0], TextObject):
            objects[0].position = position
            return objects

        # Se tem mistura, mantém os objetos separados
        return objects

    def _process_link(self, element: Tag, position: Position) -> List[LinkObject]:
        """Processa links (<a>)."""
        if not self.extract_links:
            # Se não deve extrair links, trata como texto
            text = element.get_text(strip=True)
            return [TextObject(content=text)] if text else []

        text = element.get_text(strip=True)
        href = element.get('href', '').strip()

        if not text and not href:
            return []

        # Link interno (âncora)
        if href.startswith('#'):
            link_obj = LinkObject.create_anchor(
                text=text,
                anchor_id=href[1:],
                position=position
            )
        else:
            # Link externo ou relativo
            if self.resolve_relative_urls and self.base_url and href:
                resolved_url = urljoin(self.base_url, href)
            else:
                resolved_url = href

            link_obj = LinkObject.create_from_url(
                text=text,
                url=resolved_url,
                position=position
            )

            # Adiciona metadados extras
            link_obj.metadata['title'] = element.get('title', '')
            link_obj.metadata['target'] = element.get('target', '')

        return [link_obj]

    def _process_image(self, element: Tag, position: Position) -> List[ImageObject]:
        """Processa imagens."""
        if not self.extract_images:
            # Se não deve extrair imagens, cria representação textual
            alt = element.get('alt', '')
            if alt:
                return [TextObject(content=f'[IMG: {alt}]')]
            return []

        src = element.get('src', '').strip()
        if not src:
            return []

        # Resolve URL relativa
        if self.resolve_relative_urls and self.base_url:
            resolved_src = urljoin(self.base_url, src)
        else:
            resolved_src = src

        image_obj = ImageObject.from_url(
            url=resolved_src,
            alt_text=element.get('alt', ''),
            position=position
        )

        # Adiciona metadados
        image_obj.title = element.get('title')
        image_obj.metadata['loading'] = element.get('loading', '')

        # Dimensões se especificadas
        width = element.get('width')
        height = element.get('height')
        if width and height:
            try:
                image_obj.dimensions = (int(width), int(height))
            except ValueError:
                pass

        return [image_obj]

    def _process_media(self, element: Tag, position: Position) -> List[Union[VideoObject, AudioObject]]:
        """Processa elementos de mídia (video, audio)."""
        tag_name = element.name.lower()
        src = element.get('src', '').strip()

        # Se não tem src direto, procura em <source>
        if not src:
            source_tag = element.find('source')
            if source_tag:
                src = source_tag.get('src', '').strip()

        if not src:
            return []

        # Resolve URL relativa
        if self.resolve_relative_urls and self.base_url:
            resolved_src = urljoin(self.base_url, src)
        else:
            resolved_src = src

        if tag_name == 'video':
            media_obj = VideoObject.from_url(
                url=resolved_src,
                title=element.get('title', ''),
                position=position
            )

            # Metadados específicos de vídeo
            media_obj.poster_url = element.get('poster')
            if media_obj.poster_url and self.resolve_relative_urls and self.base_url:
                media_obj.poster_url = urljoin(self.base_url, media_obj.poster_url)

            # Dimensões
            width = element.get('width')
            height = element.get('height')
            if width and height:
                try:
                    media_obj.dimensions = (int(width), int(height))
                except ValueError:
                    pass

        else:  # audio
            media_obj = AudioObject.from_url(
                url=resolved_src,
                title=element.get('title', ''),
                position=position
            )

        # Metadados comuns
        media_obj.metadata['controls'] = element.get('controls') is not None
        media_obj.metadata['autoplay'] = element.get('autoplay') is not None
        media_obj.metadata['loop'] = element.get('loop') is not None
        media_obj.metadata['muted'] = element.get('muted') is not None

        return [media_obj]

    def _process_table(self, element: Tag, position: Position) -> List[TableObject]:
        """Processa tabelas."""
        table_obj = TableObject(position=position)

        # Caption
        caption = element.find('caption')
        if caption:
            table_obj.caption = caption.get_text(strip=True)

        # Headers
        header_row = element.find('thead')
        if header_row:
            th_tags = header_row.find_all(['th', 'td'])
        else:
            # Primeira linha como header
            first_row = element.find('tr')
            if first_row:
                th_tags = first_row.find_all('th')
                if not th_tags:  # Se não tem th, não trata primeira linha como header
                    th_tags = []
            else:
                th_tags = []

        table_obj.headers = [th.get_text(strip=True) for th in th_tags]

        # Rows
        tbody = element.find('tbody') or element
        for tr in tbody.find_all('tr'):
            # Pula primeira linha se foi usada como header
            if not table_obj.headers or tr != element.find('tr'):
                cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                if cells:  # Só adiciona se não está vazia
                    table_obj.add_row(cells)

        return [table_obj]

    def _process_list(self, element: Tag, position: Position) -> List[ListObject]:
        """Processa listas (ul, ol)."""
        list_type = "ordered" if element.name.lower() == 'ol' else "unordered"
        start_num = int(element.get('start', 1))

        list_obj = ListObject(
            list_type=list_type,
            start_number=start_num,
            position=position
        )

        # Processa itens
        for li in element.find_all('li', recursive=False):  # Só filhos diretos
            li_objects = self._process_element(li)
            for obj in li_objects:
                list_obj.add_child(obj)

        return [list_obj]

    def _process_list_item(self, element: Tag, position: Position, level: int) -> List[ListItemObject]:
        """Processa itens de lista."""
        # Extrai texto direto (não de sublistas)
        text_parts = []

        for child in element.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    text_parts.append(text)
            elif isinstance(child, Tag) and child.name.lower() not in ('ul', 'ol'):
                # Processa elementos que não são sublistas
                child_objects = self._process_element(child, level + 1)
                for obj in child_objects:
                    if isinstance(obj, TextObject):
                        text_parts.append(obj.content)

        item_text = ' '.join(text_parts)

        item_obj = ListItemObject(
            content=item_text,
            position=position
        )

        # Processa sublistas
        for sublist in element.find_all(['ul', 'ol'], recursive=False):
            sublist_objects = self._process_element(sublist, level + 1)
            for obj in sublist_objects:
                item_obj.add_child(obj)

        return [item_obj]

    def _process_container(self, element: Tag, position: Position, level: int) -> List[ContentObject]:
        """Processa elementos container (div, section, etc)."""
        objects = []

        for child in element.children:
            objects.extend(self._process_element(child, level + 1))

        return objects

    def _process_generic(self, element: Tag, position: Position, level: int) -> List[ContentObject]:
        """Processa elementos genéricos."""
        objects = []

        for child in element.children:
            objects.extend(self._process_element(child, level + 1))

        return objects

    def _create_position(self, element: Tag) -> Position:
        """Cria objeto Position para um elemento."""
        self._element_counter += 1

        position = Position()
        position.element_id = element.get('id')
        position.element_class = element.get('class')

        # Tenta criar um xpath básico
        try:
            path_parts = []
            current = element
            while current and current.name:
                siblings = [sibling for sibling in current.parent.children if
                            sibling.name == current.name] if current.parent else [current]
                if len(siblings) > 1:
                    index = siblings.index(current) + 1
                    path_parts.append(f"{current.name}[{index}]")
                else:
                    path_parts.append(current.name)
                current = current.parent

            if path_parts:
                path_parts.reverse()
                position.xpath = "/" + "/".join(path_parts)
        except:
            pass  # Se falhar, deixa xpath como None

        return position

    def _remove_processed_elements(self, soup: BeautifulSoup) -> None:
        """Remove elementos que já foram processados separadamente."""
        for tag_name in self.skip_tags:
            for tag in soup.find_all(tag_name):
                tag.decompose()

    def _normalize_script_type(self, script_type: str) -> str:
        """Normaliza tipo de script."""
        script_type = script_type.lower().strip()

        if 'json' in script_type:
            return 'json'
        elif 'javascript' in script_type or script_type in ('text/javascript', 'application/javascript'):
            return 'javascript'
        elif 'module' in script_type:
            return 'module'
        else:
            return script_type


class Html(FileObject):
    """Classe HTML atualizada com suporte a objetos estruturados."""

    def get_type(self) -> str:
        return "html"

    def get_objects(self,
                    types: Optional[List[str]] = None,
                    base_url: Optional[str] = None,
                    **parser_config) -> List[ContentObject]:
        """
        Extrai objetos estruturados do HTML.

        Args:
            types: Lista de tipos a extrair (['text', 'link', 'image', etc])
            base_url: URL base para resolver URLs relativas
            **parser_config: Configurações para o parser
        """
        html_str = self.get_raw(permanent=False)

        # Configuração do parser
        config = {
            'base_url': base_url,
            'extract_scripts': True,
            'extract_styles': True,
            'extract_images': True,
            'extract_links': True,
            'resolve_relative_urls': True
        }
        config.update(parser_config)

        parser = HtmlObjectParser(**config)
        all_objects = parser.parse(html_str)

        # Filtra por tipos se especificado
        if types:
            filtered_objects = []
            for obj in all_objects:
                if obj.object_type in types:
                    filtered_objects.append(obj)
            return filtered_objects

        return all_objects

    def get_text(self, head=None, permanent: bool = False,
                 use_objects: bool = True, **config) -> str:
        """
        Extrai texto do HTML.

        Args:
            head: Limitação de linhas/caracteres
            permanent: Se deve salvar permanentemente  
            use_objects: Se deve usar o sistema de objetos (novo) ou método simples
            **config: Configurações adicionais
        """
        if not use_objects:
            # Método antigo/simples
            return self.get_text_simple(head=head, permanent=permanent)

        # Método novo usando objetos
        objects = self.get_objects(types=['text', 'heading'], **config)

        text_parts = []
        for obj in objects:
            content = obj.get_content()
            if content.strip():
                text_parts.append(content)

        text = '\n'.join(text_parts)

        # Aplica limitação de head se especificada
        if head is not None:
            text = self._apply_head_limit(text, head)

        return text

    def get_text_simple(self, head=None, permanent: bool = False) -> str:
        """Método compatível com versão anterior (extração simples)."""
        html_str = self.get_raw(permanent=permanent)
        soup = BeautifulSoup(html_str, "html.parser")
        text = soup.get_text(" ", strip=True)

        if head is not None:
            text = self._apply_head_limit(text, head)

        return text

    def _apply_head_limit(self, text: str, head) -> str:
        """Aplica limitação de head ao texto."""
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

    # Métodos auxiliares usando objetos
    def get_links(self, permanent: bool = False, **config) -> List[LinkObject]:
        """Extrai todos os links do HTML."""
        objects = self.get_objects(types=['link'], **config)
        return [obj for obj in objects if isinstance(obj, LinkObject)]

    def get_images(self, permanent: bool = False, **config) -> List[ImageObject]:
        """Extrai informações sobre imagens do HTML."""
        objects = self.get_objects(types=['image'], **config)
        return [obj for obj in objects if isinstance(obj, ImageObject)]

    def get_headings(self, permanent: bool = False, **config) -> List[HeadingObject]:
        """Extrai estrutura de cabeçalhos do HTML."""
        objects = self.get_objects(types=['heading'], **config)
        return [obj for obj in objects if isinstance(obj, HeadingObject)]

    def get_scripts(self, permanent: bool = False, **config) -> List[ScriptObject]:
        """Extrai scripts do HTML."""
        objects = self.get_objects(types=['code'], **config)
        return [obj for obj in objects if isinstance(obj, (ScriptObject, CodeObject))
                and getattr(obj, 'language', '') == 'javascript']

    def get_styles(self, permanent: bool = False, **config) -> List[StyleObject]:
        """Extrai estilos CSS do HTML."""
        objects = self.get_objects(types=['style'], **config)
        return [obj for obj in objects if isinstance(obj, StyleObject)]

    def get_tables(self, permanent: bool = False, **config) -> List[TableObject]:
        """Extrai tabelas do HTML."""
        objects = self.get_objects(types=['table'], **config)
        return [obj for obj in objects if isinstance(obj, TableObject)]