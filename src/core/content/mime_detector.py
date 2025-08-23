# src/core/content/mime_detector.py
"""
Biblioteca auxiliar para detecção robusta de MIME type e encoding.
Reutilizável por qualquer driver (Local, GDrive, URL, etc).
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Optional, Union
import mimetypes


class MimeDetectionResult:
    """Resultado da detecção de MIME type e encoding."""

    def __init__(self,
                 mime_type: str,
                 encoding: str = 'binary',
                 magic_available: bool = False,
                 detection_method: str = 'fallback'):
        self.mime_type = mime_type
        self.encoding = encoding
        self.magic_available = magic_available
        self.detection_method = detection_method

    @property
    def is_text(self) -> bool:
        return self.mime_type.startswith('text/')

    @property
    def is_binary(self) -> bool:
        return not self.is_text

    def to_dict(self) -> Dict[str, Any]:
        return {
            'mime_type': self.mime_type,
            'encoding': self.encoding,
            'is_text': self.is_text,
            'is_binary': self.is_binary,
            'magic_available': self.magic_available,
            'detection_method': self.detection_method
        }


class MimeDetector:
    """Detector robusto de MIME type e encoding com fallback inteligente."""

    def __init__(self):
        self._magic_mime = None
        self._magic_encoding = None
        self._magic_initialized = False
        self._magic_available = False

    def detect_from_file(self, file_path: Union[str, Path]) -> MimeDetectionResult:
        """Detecta MIME e encoding de um arquivo."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        # Tenta python-magic primeiro
        if self._try_init_magic():
            try:
                mime_type = self._magic_mime.from_file(str(file_path))

                encoding = 'binary'
                if mime_type.startswith('text/'):
                    raw_encoding = self._magic_encoding.from_file(str(file_path))
                    encoding = self._normalize_encoding(raw_encoding)

                return MimeDetectionResult(
                    mime_type=mime_type,
                    encoding=encoding,
                    magic_available=True,
                    detection_method='python-magic'
                )
            except Exception:
                pass  # Fallback

        # Fallback: detecção sem magic
        return self._detect_fallback(file_path)

    def detect_from_bytes(self, content: bytes, filename: str = None) -> MimeDetectionResult:
        """Detecta MIME e encoding de bytes (útil para arquivos em memória)."""

        # Tenta python-magic em bytes
        if self._try_init_magic():
            try:
                mime_type = self._magic_mime.from_buffer(content)

                encoding = 'binary'
                if mime_type.startswith('text/'):
                    raw_encoding = self._magic_encoding.from_buffer(content)
                    encoding = self._normalize_encoding(raw_encoding)

                return MimeDetectionResult(
                    mime_type=mime_type,
                    encoding=encoding,
                    magic_available=True,
                    detection_method='python-magic-buffer'
                )
            except Exception:
                pass

        # Fallback: análise de bytes + filename
        return self._detect_from_bytes_fallback(content, filename)

    def _try_init_magic(self) -> bool:
        """Tenta inicializar python-magic uma única vez."""
        if self._magic_initialized:
            return self._magic_available

        self._magic_initialized = True

        try:
            import magic

            # Tenta primeiro sem magic_file
            try:
                self._magic_mime = magic.Magic(mime=True)
                self._magic_encoding = magic.Magic(mime_encoding=True)

                # Testa se funciona com um buffer pequeno
                test_content = b"Hello World"
                self._magic_mime.from_buffer(test_content)

                self._magic_available = True
                return True

            except (OSError, Exception):
                # Tenta com magic_file explícito
                magic_file = self._find_magic_file()
                if magic_file:
                    self._magic_mime = magic.Magic(magic_file=magic_file, mime=True)
                    self._magic_encoding = magic.Magic(magic_file=magic_file, mime_encoding=True)

                    # Testa se realmente funciona
                    self._magic_mime.from_buffer(test_content)

                    self._magic_available = True
                    return True

        except (ImportError, Exception):
            pass

        self._magic_available = False
        return False

    def _find_magic_file(self) -> Optional[str]:
        """Encontra magic.mgc no ambiente atual."""
        try:
            import magic
            import sys
            from pathlib import Path

            # 1. Via módulo magic
            magic_dir = Path(magic.__file__).parent
            candidates = [
                magic_dir / "libmagic" / "magic.mgc",
                magic_dir / "magic.mgc",
                magic_dir / "data" / "magic.mgc",
            ]

            for candidate in candidates:
                if candidate.exists():
                    return str(candidate.resolve())

            # 2. Via virtual environment
            if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
                venv_root = Path(sys.prefix)

                import os
                if os.name == 'nt':  # Windows
                    venv_magic = venv_root / "Lib" / "site-packages" / "magic" / "libmagic" / "magic.mgc"
                else:  # Unix
                    venv_magic = venv_root / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages" / "magic" / "libmagic" / "magic.mgc"

                if venv_magic.exists():
                    return str(venv_magic.resolve())

            # 3. Sistema
            system_paths = [
                "/usr/share/misc/magic.mgc",
                "/usr/share/file/magic.mgc",
                "/opt/homebrew/share/misc/magic.mgc",
            ]

            for path in system_paths:
                if Path(path).exists():
                    return str(Path(path).resolve())

        except Exception:
            pass

        return None

    def _normalize_encoding(self, raw_encoding: str) -> str:
        """Normaliza encoding para Python."""
        encoding_map = {
            'utf-16le': 'utf-16-le',
            'utf-16be': 'utf-16-be',
            'utf-8': 'utf-8',
            'ascii': 'ascii',
            'us-ascii': 'ascii',
            'iso-8859-1': 'iso-8859-1',
            'windows-1252': 'windows-1252',
        }

        normalized = raw_encoding.lower().strip()
        return encoding_map.get(normalized, normalized)

    def _detect_fallback(self, file_path: Path) -> MimeDetectionResult:
        """Fallback sem python-magic."""

        # Por extensão primeiro
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            # Por análise de conteúdo
            mime_type = self._detect_mime_by_content(file_path)

        # Encoding se for texto
        encoding = 'binary'
        if mime_type.startswith('text/'):
            encoding = self._detect_encoding_by_content(file_path)

        return MimeDetectionResult(
            mime_type=mime_type,
            encoding=encoding,
            magic_available=False,
            detection_method='fallback-file'
        )

    def _detect_from_bytes_fallback(self, content: bytes, filename: str = None) -> MimeDetectionResult:
        """Fallback para detecção em bytes."""

        # Por filename se disponível
        mime_type = None
        if filename:
            mime_type, _ = mimetypes.guess_type(filename)

        # Por análise de headers
        if not mime_type:
            mime_type = self._detect_mime_by_headers(content)

        # Encoding se for texto
        encoding = 'binary'
        if mime_type.startswith('text/'):
            encoding = self._detect_encoding_by_headers(content)

        return MimeDetectionResult(
            mime_type=mime_type,
            encoding=encoding,
            magic_available=False,
            detection_method='fallback-bytes'
        )

    def _detect_mime_by_content(self, file_path: Path) -> str:
        """Detecta MIME por análise básica de conteúdo."""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)

            return self._detect_mime_by_headers(header)

        except Exception:
            return 'application/octet-stream'

    def _detect_mime_by_headers(self, content: bytes) -> str:
        """Detecta MIME por headers de arquivo."""
        if len(content) < 4:
            return 'text/plain'

        # Signatures conhecidas
        if content.startswith(b'%PDF'):
            return 'application/pdf'
        elif content.startswith(b'\xff\xd8\xff'):
            return 'image/jpeg'
        elif content.startswith(b'\x89PNG'):
            return 'image/png'
        elif content.startswith(b'GIF8'):
            return 'image/gif'
        elif content.startswith(b'PK\x03\x04'):
            return 'application/zip'
        elif content.startswith(b'\x00\x00\x01\x00'):
            return 'image/x-icon'
        else:
            # Assume texto se tem caracteres imprimíveis
            try:
                content[:100].decode('utf-8', errors='strict')
                return 'text/plain'
            except UnicodeDecodeError:
                return 'application/octet-stream'

    def _detect_encoding_by_content(self, file_path: Path) -> str:
        """Detecta encoding por análise de arquivo."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read(4)

            return self._detect_encoding_by_headers(content)

        except Exception:
            return 'utf-8'

    def _detect_encoding_by_headers(self, content: bytes) -> str:
        """Detecta encoding por BOM e heurística."""
        if len(content) < 2:
            return 'utf-8'

        # BOM detection
        if content.startswith(b'\xff\xfe'):
            return 'utf-16-le'
        elif content.startswith(b'\xfe\xff'):
            return 'utf-16-be'
        elif content.startswith(b'\xef\xbb\xbf'):
            return 'utf-8-sig'
        else:
            # Heurística: tenta UTF-8, fallback Windows-1252
            try:
                content.decode('utf-8')
                return 'utf-8'
            except UnicodeDecodeError:
                return 'windows-1252'


# Instância global (singleton pattern)
_mime_detector = None


def get_mime_detector() -> MimeDetector:
    """Retorna instância singleton do detector."""
    global _mime_detector
    if _mime_detector is None:
        _mime_detector = MimeDetector()
    return _mime_detector


# Funções de conveniência
def detect_file_type(file_path: Union[str, Path]) -> MimeDetectionResult:
    """Detecta tipo de arquivo - função de conveniência."""
    return get_mime_detector().detect_from_file(file_path)


def detect_bytes_type(content: bytes, filename: str = None) -> MimeDetectionResult:
    """Detecta tipo de bytes - função de conveniência."""
    return get_mime_detector().detect_from_bytes(content, filename)