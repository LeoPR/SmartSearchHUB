# src/core/content/drivers.py
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union, BinaryIO, Any, Dict
from urllib.parse import urlparse
import io


class ContentDriver(ABC):
    """Interface base para drivers de conteúdo."""

    @abstractmethod
    def can_handle(self, source: Any) -> bool:
        """Verifica se o driver pode processar a fonte."""
        pass

    @abstractmethod
    def get_content(self) -> bytes:
        """Obtém o conteúdo como bytes."""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Obtém metadados da fonte."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se a fonte está disponível."""
        pass

    def get_content_as_text(self, encoding: str = 'auto') -> str:
        """Converte conteúdo para texto com detecção automática de encoding."""
        content_bytes = self.get_content()

        if encoding == 'auto':
            detected_encoding = self.detect_encoding(content_bytes)
        else:
            detected_encoding = encoding

        try:
            result = content_bytes.decode(detected_encoding)

            if result.startswith('\ufeff'):
                result = result.lstrip('\ufeff')

            return result
        except UnicodeDecodeError:
            return content_bytes.decode(detected_encoding, errors='ignore')


@dataclass
class LocalFileDriver(ContentDriver):
    """Driver para arquivos locais com detecção robusta de tipo."""

    file_path: Union[str, Path]
    _file_info: Optional[Dict[str, Any]] = field(default=None, init=False)

    def __post_init__(self):
        self.file_path = Path(self.file_path)

    def get_file_info(self) -> Dict[str, Any]:
        """Analisa arquivo usando detector auxiliar."""
        if self._file_info is not None:
            return self._file_info

        if not self.is_available():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.file_path}")

        # USA A BIBLIOTECA AUXILIAR
        from .mime_detector import detect_file_type

        detection_result = detect_file_type(self.file_path)

        # Informações do arquivo
        stat = self.file_path.stat()

        self._file_info = {
            **detection_result.to_dict(),
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'name': self.file_path.name,
            'extension': self.file_path.suffix.lower(),
        }

        return self._file_info

    def get_content_as_text(self, encoding: str = 'auto') -> str:
        """Obtém conteúdo como texto."""
        file_info = self.get_file_info()

        if not file_info['is_text']:
            raise ValueError(
                f"Arquivo '{self.file_path.name}' é {file_info['mime_type']}, não texto"
            )

        detected_encoding = file_info['encoding'] if encoding == 'auto' else encoding

        try:
            with open(self.file_path, 'r', encoding=detected_encoding) as f:
                content = f.read()

            # Remove BOM se presente
            if content.startswith('\ufeff'):
                content = content[1:]

            return content

        except UnicodeDecodeError:
            with open(self.file_path, 'r', encoding=detected_encoding, errors='ignore') as f:
                content = f.read()

            if content.startswith('\ufeff'):
                content = content[1:]

            return content

    def can_handle(self, source: Any) -> bool:
        """Verifica se o driver pode processar a fonte."""
        if isinstance(source, (str, Path)):
            path = Path(source)
            return path.exists() and path.is_file()
        return False

    def get_content(self) -> bytes:
        """Obtém o conteúdo como bytes."""
        if not self.is_available():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.file_path}")
        return self.file_path.read_bytes()

    def get_metadata(self) -> Dict[str, Any]:
        """Obtém metadados da fonte."""
        try:
            return self.get_file_info()
        except Exception:
            # Fallback para versão simples se get_file_info falhar
            if not self.is_available():
                return {}

            stat = self.file_path.stat()
            return {
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'name': self.file_path.name,
                'extension': self.file_path.suffix,
                'path': str(self.file_path.absolute()),
            }

    def is_available(self) -> bool:
        """Verifica se a fonte está disponível."""
        return self.file_path.exists() and self.file_path.is_file()

@dataclass
class UrlDriver(ContentDriver):
    """Driver para URLs remotas."""

    url: str
    timeout: int = 30
    headers: Optional[Dict[str, str]] = None
    _cached_content: Optional[bytes] = None
    _cached_metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.headers:
            self.headers = {
                'User-Agent': 'SmartSearchHUB/1.0'
            }

    def can_handle(self, source: Any) -> bool:
        if isinstance(source, str):
            try:
                parsed = urlparse(source)
                return parsed.scheme in ('http', 'https')
            except:
                return False
        return False

    def get_content(self) -> bytes:
        if self._cached_content is not None:
            return self._cached_content

        try:
            import requests
            response = requests.get(
                self.url,
                timeout=self.timeout,
                headers=self.headers
            )
            response.raise_for_status()
            self._cached_content = response.content

            # Cache metadados também
            self._cached_metadata = {
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'content_length': len(response.content),
                'url': self.url,
                'final_url': response.url,  # Após redirects
                'headers': dict(response.headers)
            }

            return self._cached_content
        except Exception as e:
            raise ConnectionError(f"Failed to fetch {self.url}: {str(e)}")

    def get_metadata(self) -> Dict[str, Any]:
        if self._cached_metadata is not None:
            return self._cached_metadata

        # Se não tem cache, faz uma requisição HEAD primeiro
        try:
            import requests
            response = requests.head(
                self.url,
                timeout=self.timeout,
                headers=self.headers,
                allow_redirects=True
            )

            return {
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'content_length': response.headers.get('content-length'),
                'url': self.url,
                'final_url': response.url,
                'headers': dict(response.headers)
            }
        except Exception:
            return {'url': self.url, 'available': False}

    def is_available(self) -> bool:
        try:
            metadata = self.get_metadata()
            return metadata.get('status_code', 0) < 400
        except:
            return False

    def clear_cache(self):
        """Limpa cache do conteúdo."""
        self._cached_content = None
        self._cached_metadata = None


@dataclass
class InlineContentDriver(ContentDriver):
    """Driver para conteúdo inline (já em memória)."""

    content: Union[str, bytes]
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def can_handle(self, source: Any) -> bool:
        return isinstance(source, (str, bytes))

    def get_content(self) -> bytes:
        if isinstance(self.content, str):
            return self.content.encode('utf-8')
        return self.content

    def get_metadata(self) -> Dict[str, Any]:
        base_metadata = {
            'size': len(self.get_content()),
            'type': 'inline'
        }
        base_metadata.update(self.metadata)
        return base_metadata

    def is_available(self) -> bool:
        return True


class DriverFactory:
    """Factory para criar drivers baseado na fonte."""

    @staticmethod
    def create_driver(source: Any, **kwargs) -> ContentDriver:
        """Cria o driver apropriado para a fonte."""

        # Tenta URL primeiro
        url_driver = UrlDriver(url="", **kwargs)
        if url_driver.can_handle(source):
            return UrlDriver(url=source, **kwargs)

        # Tenta arquivo local
        file_driver = LocalFileDriver(file_path="")
        if file_driver.can_handle(source):
            return LocalFileDriver(file_path=source)

        # Fallback para conteúdo inline
        return InlineContentDriver(content=source, **kwargs)

    @staticmethod
    def create_url_driver(url: str, **kwargs) -> UrlDriver:
        """Cria driver específico para URL."""
        return UrlDriver(url=url, **kwargs)

    @staticmethod
    def create_file_driver(path: Union[str, Path]) -> LocalFileDriver:
        """Cria driver específico para arquivo."""
        return LocalFileDriver(file_path=path)

    @staticmethod
    def create_inline_driver(content: Union[str, bytes], **metadata) -> InlineContentDriver:
        """Cria driver para conteúdo inline."""
        return InlineContentDriver(content=content, metadata=metadata)