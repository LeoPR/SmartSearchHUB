# src/core/content/media.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, Any, Dict, Union
from pathlib import Path
from .base import ContentObject, ObjectType
from .link import UrlObject
from .drivers import ContentDriver, DriverFactory


@dataclass
class ImageObject(ContentObject):
    """Objeto para imagens."""

    alt_text: str = ""
    title: Optional[str] = None
    dimensions: Optional[Tuple[int, int]] = None  # (width, height)
    format: Optional[str] = None  # jpeg, png, gif, etc.
    size_bytes: Optional[int] = None

    # Fonte da imagem (pode ser URL, arquivo local, ou inline)
    source: Optional[Union[UrlObject, str, Path]] = None

    # Driver para acessar o conteúdo
    _driver: Optional[ContentDriver] = field(default=None, init=False, repr=False)

    # Cache de dados da imagem
    _cached_content: Optional[bytes] = field(default=None, init=False, repr=False)

    object_type: str = ObjectType.IMAGE

    def get_content(self) -> str:
        """Retorna representação textual da imagem."""
        if self.alt_text:
            return f"[IMG: {self.alt_text}]"
        elif self.title:
            return f"[IMG: {self.title}]"
        elif isinstance(self.source, UrlObject):
            filename = self._extract_filename_from_url(self.source.url)
            return f"[IMG: {filename}]" if filename else "[IMG]"
        elif isinstance(self.source, (str, Path)):
            filename = Path(self.source).name
            return f"[IMG: {filename}]"
        else:
            return "[IMG]"

    def get_raw_data(self) -> Dict[str, Any]:
        return {
            'alt_text': self.alt_text,
            'title': self.title,
            'dimensions': self.dimensions,
            'format': self.format,
            'size_bytes': self.size_bytes,
            'source': self._serialize_source()
        }

    def _serialize_source(self) -> Dict[str, Any]:
        """Serializa a fonte da imagem."""
        if isinstance(self.source, UrlObject):
            return {'type': 'url', 'data': self.source.to_dict()}
        elif isinstance(self.source, (str, Path)):
            return {'type': 'file', 'data': str(self.source)}
        else:
            return {'type': 'unknown', 'data': None}

    def _extract_filename_from_url(self, url: str) -> Optional[str]:
        """Extrai nome do arquivo de uma URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            filename = parsed.path.split('/')[-1].split('?')[0]
            return filename if filename else None
        except:
            return None

    def get_driver(self) -> ContentDriver:
        """Obtém driver para acessar o conteúdo da imagem."""
        if not self._driver:
            if isinstance(self.source, UrlObject):
                self._driver = self.source.get_driver()
            elif self.source:
                self._driver = DriverFactory.create_driver(self.source)
            else:
                raise ValueError("No source defined for image")
        return self._driver

    def is_available(self) -> bool:
        """Verifica se a imagem está disponível."""
        try:
            driver = self.get_driver()
            return driver.is_available()
        except:
            return False

    def get_image_data(self, use_cache: bool = True) -> bytes:
        """Obtém os dados binários da imagem."""
        if use_cache and self._cached_content is not None:
            return self._cached_content

        driver = self.get_driver()
        content = driver.get_content()

        if use_cache:
            self._cached_content = content

        # Atualiza metadados se ainda não temos
        if not self.size_bytes:
            self.size_bytes = len(content)

        return content

    def analyze_image(self) -> Dict[str, Any]:
        """Analisa a imagem e extrai metadados (requer PIL/Pillow)."""
        try:
            from PIL import Image
            import io

            image_data = self.get_image_data()
            with Image.open(io.BytesIO(image_data)) as img:
                analysis = {
                    'format': img.format.lower() if img.format else None,
                    'mode': img.mode,
                    'size': img.size,  # (width, height)
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }

                # Atualiza propriedades do objeto
                self.format = analysis['format']
                self.dimensions = analysis['size']

                return analysis

        except ImportError:
            return {'error': 'PIL/Pillow not available'}
        except Exception as e:
            return {'error': str(e)}

    def save_to_file(self, path: Union[str, Path]) -> None:
        """Salva a imagem em um arquivo."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        image_data = self.get_image_data()
        path.write_bytes(image_data)

    def clear_cache(self):
        """Limpa cache da imagem."""
        self._cached_content = None

    @classmethod
    def from_url(cls, url: str, alt_text: str = "", **kwargs) -> ImageObject:
        """Cria ImageObject a partir de uma URL."""
        url_obj = UrlObject(url=url, target_type='image')
        return cls(source=url_obj, alt_text=alt_text, **kwargs)

    @classmethod
    def from_file(cls, path: Union[str, Path], alt_text: str = "", **kwargs) -> ImageObject:
        """Cria ImageObject a partir de um arquivo local."""
        return cls(source=path, alt_text=alt_text, **kwargs)

    @classmethod
    def from_data(cls, data: bytes, alt_text: str = "", format: str = None, **kwargs) -> ImageObject:
        """Cria ImageObject a partir de dados binários."""
        driver = DriverFactory.create_inline_driver(data, content_type=f'image/{format}' if format else None)
        obj = cls(alt_text=alt_text, format=format, **kwargs)
        obj._driver = driver
        obj.size_bytes = len(data)
        return obj


@dataclass
class VideoObject(ContentObject):
    """Objeto para vídeos."""

    title: Optional[str] = None
    duration: Optional[float] = None  # em segundos
    dimensions: Optional[Tuple[int, int]] = None  # (width, height)
    format: Optional[str] = None  # mp4, webm, etc.
    size_bytes: Optional[int] = None
    poster_url: Optional[str] = None  # URL da thumbnail

    # Fonte do vídeo
    source: Optional[Union[UrlObject, str, Path]] = None

    # Driver para acessar o conteúdo
    _driver: Optional[ContentDriver] = field(default=None, init=False, repr=False)

    object_type: str = ObjectType.VIDEO

    def get_content(self) -> str:
        """Retorna representação textual do vídeo."""
        if self.title:
            return f"[VIDEO: {self.title}]"
        elif isinstance(self.source, UrlObject):
            filename = self._extract_filename_from_url(self.source.url)
            return f"[VIDEO: {filename}]" if filename else "[VIDEO]"
        elif isinstance(self.source, (str, Path)):
            filename = Path(self.source).name
            return f"[VIDEO: {filename}]"
        else:
            return "[VIDEO]"

    def get_raw_data(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'duration': self.duration,
            'dimensions': self.dimensions,
            'format': self.format,
            'size_bytes': self.size_bytes,
            'poster_url': self.poster_url,
            'source': self._serialize_source()
        }

    def _serialize_source(self) -> Dict[str, Any]:
        """Serializa a fonte do vídeo."""
        if isinstance(self.source, UrlObject):
            return {'type': 'url', 'data': self.source.to_dict()}
        elif isinstance(self.source, (str, Path)):
            return {'type': 'file', 'data': str(self.source)}
        else:
            return {'type': 'unknown', 'data': None}

    def _extract_filename_from_url(self, url: str) -> Optional[str]:
        """Extrai nome do arquivo de uma URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            filename = parsed.path.split('/')[-1].split('?')[0]
            return filename if filename else None
        except:
            return None

    def get_driver(self) -> ContentDriver:
        """Obtém driver para acessar o conteúdo do vídeo."""
        if not self._driver:
            if isinstance(self.source, UrlObject):
                self._driver = self.source.get_driver()
            elif self.source:
                self._driver = DriverFactory.create_driver(self.source)
            else:
                raise ValueError("No source defined for video")
        return self._driver

    def is_available(self) -> bool:
        """Verifica se o vídeo está disponível."""
        try:
            driver = self.get_driver()
            return driver.is_available()
        except:
            return False

    def get_video_data(self) -> bytes:
        """Obtém os dados binários do vídeo."""
        driver = self.get_driver()
        content = driver.get_content()

        if not self.size_bytes:
            self.size_bytes = len(content)

        return content

    def get_duration_formatted(self) -> str:
        """Retorna duração formatada (MM:SS ou HH:MM:SS)."""
        if not self.duration:
            return "00:00"

        total_seconds = int(self.duration)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    @classmethod
    def from_url(cls, url: str, title: str = "", **kwargs) -> VideoObject:
        """Cria VideoObject a partir de uma URL."""
        url_obj = UrlObject(url=url, target_type='video')
        return cls(source=url_obj, title=title, **kwargs)

    @classmethod
    def from_file(cls, path: Union[str, Path], title: str = "", **kwargs) -> VideoObject:
        """Cria VideoObject a partir de um arquivo local."""
        return cls(source=path, title=title, **kwargs)


@dataclass
class AudioObject(ContentObject):
    """Objeto para áudios."""

    title: Optional[str] = None
    artist: Optional[str] = None
    duration: Optional[float] = None  # em segundos
    format: Optional[str] = None  # mp3, wav, etc.
    size_bytes: Optional[int] = None
    bitrate: Optional[int] = None  # em kbps

    # Fonte do áudio
    source: Optional[Union[UrlObject, str, Path]] = None

    # Driver para acessar o conteúdo
    _driver: Optional[ContentDriver] = field(default=None, init=False, repr=False)

    object_type: str = ObjectType.AUDIO

    def get_content(self) -> str:
        """Retorna representação textual do áudio."""
        if self.title and self.artist:
            return f"[AUDIO: {self.artist} - {self.title}]"
        elif self.title:
            return f"[AUDIO: {self.title}]"
        elif isinstance(self.source, UrlObject):
            filename = self._extract_filename_from_url(self.source.url)
            return f"[AUDIO: {filename}]" if filename else "[AUDIO]"
        elif isinstance(self.source, (str, Path)):
            filename = Path(self.source).name
            return f"[AUDIO: {filename}]"
        else:
            return "[AUDIO]"

    def get_raw_data(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'artist': self.artist,
            'duration': self.duration,
            'format': self.format,
            'size_bytes': self.size_bytes,
            'bitrate': self.bitrate,
            'source': self._serialize_source()
        }

    def _serialize_source(self) -> Dict[str, Any]:
        """Serializa a fonte do áudio."""
        if isinstance(self.source, UrlObject):
            return {'type': 'url', 'data': self.source.to_dict()}
        elif isinstance(self.source, (str, Path)):
            return {'type': 'file', 'data': str(self.source)}
        else:
            return {'type': 'unknown', 'data': None}

    def _extract_filename_from_url(self, url: str) -> Optional[str]:
        """Extrai nome do arquivo de uma URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            filename = parsed.path.split('/')[-1].split('?')[0]
            return filename if filename else None
        except:
            return None

    def get_driver(self) -> ContentDriver:
        """Obtém driver para acessar o conteúdo do áudio."""
        if not self._driver:
            if isinstance(self.source, UrlObject):
                self._driver = self.source.get_driver()
            elif self.source:
                self._driver = DriverFactory.create_driver(self.source)
            else:
                raise ValueError("No source defined for audio")
        return self._driver

    def is_available(self) -> bool:
        """Verifica se o áudio está disponível."""
        try:
            driver = self.get_driver()
            return driver.is_available()
        except:
            return False

    def get_audio_data(self) -> bytes:
        """Obtém os dados binários do áudio."""
        driver = self.get_driver()
        content = driver.get_content()

        if not self.size_bytes:
            self.size_bytes = len(content)

        return content

    def get_duration_formatted(self) -> str:
        """Retorna duração formatada (MM:SS)."""
        if not self.duration:
            return "00:00"

        total_seconds = int(self.duration)
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        return f"{minutes:02d}:{seconds:02d}"

    @classmethod
    def from_url(cls, url: str, title: str = "", **kwargs) -> AudioObject:
        """Cria AudioObject a partir de uma URL."""
        url_obj = UrlObject(url=url, target_type='audio')
        return cls(source=url_obj, title=title, **kwargs)

    @classmethod
    def from_file(cls, path: Union[str, Path], title: str = "", **kwargs) -> AudioObject:
        """Cria AudioObject a partir de um arquivo local."""
        return cls(source=path, title=title, **kwargs)