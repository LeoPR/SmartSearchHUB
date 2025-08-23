import pytest
from unittest.mock import Mock, patch
from pathlib import Path
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
        """Testa conteúdo português com detecção automática."""
        test_file = tmp_path / "test_pt.txt"
        content = "configuração técnica: açúcar, não, coração"
        test_file.write_text(content, encoding='utf-8')

        driver = LocalFileDriver(test_file)
        result = driver.get_content_as_text(encoding='auto')
        assert result == content

    def test_get_content_raw_bytes(self, tmp_path):
        """Testa leitura de bytes brutos."""
        test_file = tmp_path / "test_bytes.txt"
        content = "teste de bytes"
        test_file.write_text(content, encoding='utf-8')

        driver = LocalFileDriver(test_file)
        result = driver.get_content()

        assert isinstance(result, bytes)
        assert result.decode('utf-8') == content

    def test_file_not_found(self, tmp_path):
        """Testa comportamento com arquivo inexistente."""
        missing_file = tmp_path / "nao_existe.txt"

        driver = LocalFileDriver(missing_file)
        assert not driver.can_handle(missing_file)
        assert not driver.is_available()

    def test_get_metadata(self, sample_text_files):
        """Testa obtenção de metadados usando fixture."""
        driver = LocalFileDriver(sample_text_files['utf8'])
        metadata = driver.get_metadata()

        assert isinstance(metadata, dict)
        assert 'size' in metadata
        assert metadata['size'] > 0


class TestUrlDriver:
    @patch('requests.get')
    def test_fetch_url_success(self, mock_get):
        """Testa download de URL com sucesso."""
        mock_response = Mock()
        mock_response.content = b"conteudo html"
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.url = "https://example.com"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        driver = UrlDriver("https://example.com")
        content = driver.get_content()

        assert content == b"conteudo html"
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_fetch_url_with_encoding(self, mock_get):
        """Testa download com encoding específico."""
        mock_response = Mock()
        mock_response.content = "configuração".encode('utf-8')
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html; charset=utf-8'}
        mock_response.url = "https://example.com"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        driver = UrlDriver("https://example.com")
        content = driver.get_content()

        assert isinstance(content, bytes)
        assert "configuração".encode('utf-8') == content

    @patch('requests.head')
    def test_get_metadata(self, mock_head):
        """Testa obtenção de metadados via HEAD request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'content-type': 'text/html',
            'content-length': '1234'
        }
        mock_response.url = "https://example.com"
        mock_response.raise_for_status.return_value = None
        mock_head.return_value = mock_response

        driver = UrlDriver("https://example.com")
        metadata = driver.get_metadata()

        assert metadata['status_code'] == 200
        assert metadata['content_type'] == 'text/html'
        assert metadata['url'] == "https://example.com"
        mock_head.assert_called_once()

    @patch('requests.head')
    def test_is_available(self, mock_head):
        """Testa verificação de disponibilidade."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_head.return_value = mock_response

        driver = UrlDriver("https://example.com")
        assert driver.is_available() == True
        mock_head.assert_called_once()

    @patch('requests.head')
    def test_is_not_available(self, mock_head):
        """Testa URL não disponível."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {}
        mock_head.return_value = mock_response

        driver = UrlDriver("https://example.com/404")
        assert driver.is_available() == False
        mock_head.assert_called_once()

    def test_can_handle_url(self):
        """Testa identificação de URLs válidas."""
        driver = UrlDriver("https://example.com")

        assert driver.can_handle("https://example.com") == True
        assert driver.can_handle("http://example.com") == True
        assert driver.can_handle("ftp://example.com") == False
        assert driver.can_handle("/local/path") == False

    @patch('requests.get')
    def test_fetch_url_with_error(self, mock_get):
        """Testa tratamento de erro HTTP."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 500 Error")
        mock_get.return_value = mock_response

        driver = UrlDriver("https://example.com/error")

        with pytest.raises(ConnectionError):
            driver.get_content()


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

    def test_string_content_with_portuguese(self):
        """Testa string com caracteres portugueses."""
        content = "configuração técnica"
        driver = InlineContentDriver(content)

        result = driver.get_content()
        assert isinstance(result, bytes)
        assert result.decode('utf-8') == content

    def test_get_metadata(self):
        """Testa obtenção de metadados."""
        content = "teste de conteúdo"
        driver = InlineContentDriver(content, metadata={'source': 'test'})

        metadata = driver.get_metadata()
        assert metadata['size'] == len(content.encode('utf-8'))
        assert metadata['type'] == 'inline'
        assert metadata['source'] == 'test'

    def test_can_handle_various_types(self):
        """Testa identificação de diferentes tipos de conteúdo."""
        driver = InlineContentDriver("")

        assert driver.can_handle("string") == True
        assert driver.can_handle(b"bytes") == True
        assert driver.can_handle(123) == False
        assert driver.can_handle(None) == False


class TestDriverFactoryBasic:
    """Testes básicos para factory de drivers (sem importar a factory diretamente)."""

    def test_local_driver_creation(self, tmp_path):
        """Testa criação de driver local."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("conteudo", encoding='utf-8')

        driver = LocalFileDriver(test_file)
        assert driver.can_handle(test_file)
        assert isinstance(driver, LocalFileDriver)

    def test_url_driver_creation(self):
        """Testa criação de driver de URL."""
        url = "https://example.com"
        driver = UrlDriver(url)
        assert driver.can_handle(url)
        assert isinstance(driver, UrlDriver)

    def test_inline_driver_creation(self):
        """Testa criação de driver inline."""
        content = "teste"
        driver = InlineContentDriver(content)
        assert driver.can_handle(content)
        assert isinstance(driver, InlineContentDriver)