# src/core/content/link.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Any, Dict
from urllib.parse import urlparse, urljoin
from .base import ContentObject, ObjectType
from .drivers import ContentDriver, DriverFactory


@dataclass
class UrlObject(ContentObject):
    """Objeto para URLs/links."""

    url: str = ""
    title: Optional[str] = None
    target_type: Optional[str] = None  # 'image', 'document', 'video', etc.
    is_external: bool = True
    is_accessible: Optional[bool] = None  # None = não testado ainda

    # Driver para acessar o conteúdo da URL
    _driver: Optional[ContentDriver] = field(default=None, init=False, repr=False)

    object_type: str = ObjectType.URL

    def __post_init__(self):
        super().__post_init__()
        self._analyze_url()

    def _analyze_url(self):
        """Analisa a URL e define propriedades básicas."""
        if not self.url:
            return

        try:
            parsed = urlparse(self.url)

            # Determina se é externa
            self.is_external = bool(parsed.scheme and parsed.netloc)

            # Tenta determinar o tipo pelo path/extensão
            if not self.target_type:
                path = parsed.path.lower()
                if any(path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
                    self.target_type = 'image'
                elif any(path.endswith(ext) for ext in ['.pdf', '.doc', '.docx']):
                    self.target_type = 'document'
                elif any(path.endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.webm']):
                    self.target_type = 'video'
                elif any(path.endswith(ext) for ext in ['.mp3', '.wav', '.ogg']):
                    self.target_type = 'audio'
                else:
                    self.target_type = 'webpage'

        except Exception:
            pass  # URL malformada, mantém valores padrão

    def get_content(self) -> str:
        """Retorna representação textual da URL."""
        if self.title and self.title != self.url:
            return f"{self.title} ({self.url})"
        return self.url

    def get_raw_data(self) -> Dict[str, Any]:
        return {
            'url': self.url,
            'title': self.title,
            'target_type': self.target_type,
            'is_external': self.is_external,
            'is_accessible': self.is_accessible
        }

    def get_driver(self) -> ContentDriver:
        """Obtém driver para acessar o conteúdo da URL."""
        if not self._driver:
            self._driver = DriverFactory.create_url_driver(self.url)
        return self._driver

    def test_accessibility(self) -> bool:
        """Testa se a URL está acessível."""
        if self.is_accessible is not None:
            return self.is_accessible

        try:
            driver = self.get_driver()
            self.is_accessible = driver.is_available()
        except Exception:
            self.is_accessible = False

        return self.is_accessible

    def fetch_content(self) -> bytes:
        """Baixa o conteúdo da URL."""
        if not self.is_external:
            raise ValueError("Cannot fetch content from non-external URL")

        driver = self.get_driver()
        return driver.get_content()

    def fetch_metadata(self) -> Dict[str, Any]:
        """Obtém metadados da URL."""
        driver = self.get_driver()
        return driver.get_metadata()

    def resolve_relative(self, base_url: str) -> str:
        """Resolve URL relativa baseada numa URL base."""
        if self.is_external:
            return self.url
        return urljoin(base_url, self.url)

    def update_url(self, new_url: str):
        """Atualiza a URL e reanalisa."""
        self.url = new_url
        self._driver = None  # Reset driver
        self.is_accessible = None  # Reset status
        self._analyze_url()


@dataclass
class LinkObject(ContentObject):
    """Objeto para links HTML (combinação de texto + URL)."""

    text: str = ""
    url_object: Optional[UrlObject] = None
    anchor_id: Optional[str] = None  # href="#section"

    object_type: str = ObjectType.LINK

    def get_content(self) -> str:
        """Retorna o texto do link."""
        return self.text

    def get_raw_data(self) -> Dict[str, Any]:
        return {
            'text': self.text,
            'url': self.url_object.url if self.url_object else None,
            'url_object': self.url_object.to_dict() if self.url_object else None,
            'anchor_id': self.anchor_id
        }

    def get_url(self) -> Optional[str]:
        """Retorna a URL do link."""
        return self.url_object.url if self.url_object else None

    def is_internal_anchor(self) -> bool:
        """Verifica se é um link interno (#section)."""
        return bool(self.anchor_id and not self.url_object)

    def is_external(self) -> bool:
        """Verifica se o link é externo."""
        return bool(self.url_object and self.url_object.is_external)

    def test_accessibility(self) -> bool:
        """Testa se o link está acessível."""
        if not self.url_object:
            return True  # Links internos são sempre "acessíveis"
        return self.url_object.test_accessibility()

    def fetch_linked_content(self) -> Optional[bytes]:
        """Baixa o conteúdo do link."""
        if not self.url_object or not self.url_object.is_external:
            return None
        return self.url_object.fetch_content()

    @classmethod
    def create_from_url(cls, text: str, url: str, **kwargs) -> LinkObject:
        """Cria LinkObject a partir de texto e URL."""
        url_obj = UrlObject(url=url)
        return cls(text=text, url_object=url_obj, **kwargs)

    @classmethod
    def create_anchor(cls, text: str, anchor_id: str, **kwargs) -> LinkObject:
        """Cria LinkObject para link interno (#anchor)."""
        return cls(text=text, anchor_id=anchor_id, **kwargs)