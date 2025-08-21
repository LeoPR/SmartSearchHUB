import pytest
from unittest.mock import Mock, patch
from src.core.io.html import Html, HtmlObjectParser
from src.core.content.text import HeadingObject
from src.core.content.link import LinkObject

class TestHtmlParser:
    def test_extract_headings(self):
        """Testa extração de cabeçalhos de HTML simples."""
        html_content = """
        <html><body>
            <h1>Título Principal</h1>
            <h2>Subtítulo</h2>
            <p>Texto normal</p>
        </body></html>
        """

        parser = HtmlObjectParser()
        objects = parser.parse(html_content)

        headings = [obj for obj in objects if obj.object_type == 'heading']
        assert len(headings) == 2
        assert headings[0].level == 1
        assert headings[0].content == "Título Principal"
        assert headings[1].level == 2
        assert headings[1].content == "Subtítulo"

    def test_extract_links(self):
        """Testa extração de links."""
        html_content = """
        <html><body>
            <a href="https://example.com">Link Externo</a>
            <a href="#section">Link Interno</a>
            <a href="page.html">Link Relativo</a>
        </body></html>
        """

        parser = HtmlObjectParser(base_url="https://test.com/")
        objects = parser.parse(html_content)

        links = [obj for obj in objects if obj.object_type == 'link']
        assert len(links) == 3

        # Verifica link externo
        external_link = next(l for l in links if l.text == "Link Externo")
        assert external_link.is_external()

        # Verifica link interno
        internal_link = next(l for l in links if l.text == "Link Interno")
        assert internal_link.is_internal_anchor()


class TestHtmlFile:
    def test_get_text_with_mock(self):
        """Testa extração de texto usando mock."""
        # Mock do arquivo base
        mock_base = Mock()
        mock_base.get_raw.return_value = "<html><body><p>Teste</p></body></html>"
        mock_base.id = "test123"
        mock_base.name = "test.html"
        mock_base.mimetype = "text/html"

        html_file = Html(mock_base)
        text = html_file.get_text_simple()

        assert "Teste" in text
        mock_base.get_raw.assert_called_once()