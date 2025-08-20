import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from src.core.content.drivers import LocalFileDriver, UrlDriver, InlineContentDriver


class TestLocalFileDriver:
    def test_can_handle_existing_file(self, tmp_path):
        """Testa se driver identifica arquivo existente."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("conteúdo teste")

        driver = LocalFileDriver(test_file)
        assert driver.can_handle(test_file)
        assert driver.is_available()

    def test_get_content(self, tmp_path):
        """Testa leitura de conteúdo."""
        test_file = tmp_path / "test.txt"
        content = "conteúdo de teste"
        test_file.write_text(content)

        driver = LocalFileDriver(test_file)
        assert driver.get_content_as_text() == content


class TestUrlDriver:
    @patch('requests.get')
    def test_fetch_url_success(self, mock_get):
        """Testa download de URL com sucesso."""
        mock_response = Mock()
        mock_response.content = b"conteudo html"
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
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