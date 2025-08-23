import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import requests  # Adicionado
from src.core.content.drivers import LocalFileDriver, UrlDriver, InlineContentDriver

class TestLocalFileDriver:
    def test_can_handle_existing_file(self, tmp_path):
        """Testa se driver identifica arquivo existente."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("conteudo teste", encoding='utf-8')

        driver = LocalFileDriver(test_file)
        assert driver.can_handle(test_file)
        assert driver.is_available()

    def test_get_content(self, tmp_path):
        """Testa leitura de conteúdo."""
        test_file = tmp_path / "test.txt"
        content = "conteudo de teste"  # Sem acento para compatibilidade
        test_file.write_text(content, encoding='utf-8')

        driver = LocalFileDriver(test_file)
        result = driver.get_content_as_text(encoding='utf-8')
        assert result == content

    def test_get_content_with_unicode(self, tmp_path):
        """Testa conteúdo com caracteres especiais."""
        test_file = tmp_path / "test_unicode.txt"
        content = "teste com acentos: ção, não, coração"
        test_file.write_text(content, encoding='utf-8')

        driver = LocalFileDriver(test_file)
        result = driver.get_content_as_text(encoding='utf-8')
        assert result == content

    def test_get_content_with_portuguese(self, tmp_path):
        test_file = tmp_path / "test_pt.txt"
        content = "configuração técnica: açúcar, não, coração"
        test_file.write_text(content, encoding='utf-8')

        driver = LocalFileDriver(test_file)
        result = driver.get_content_as_text(encoding='auto')
        assert result == content

class TestUrlDriver:
    @patch('requests.get')
    def test_fetch_url_success(self, mock_get):
        """Testa download de URL com sucesso."""
        mock_response = Mock()
        mock_response.content = b"conteudo html"
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.url = "https://example.com"  # Adicionado
        mock_get.return_value = mock_response

        driver = UrlDriver("https://example.com")
        content = driver.get_content()

        assert content == b"conteudo html"
        mock_get.assert_called_once()

class TestInlineContentDriver:
    def test_string_content(self):
        """Testa conteúdo string."""
        driver = InlineContentDriver("teste")
        assert driver.get_content() == b"teste"
        assert driver.is_available()

    def test_bytes_content(self):
        """Testa conteúdo em bytes."""
        content = b"conte\xc3\xbado"  # "conteúdo" em UTF-8
        driver = InlineContentDriver(content)
        assert driver.get_content() == content
        assert driver.is_available()