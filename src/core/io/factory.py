# src/core/io/factory.py
from __future__ import annotations
from .baseobj import FileObject
from .html import Html
from .pdf import Pdf
from .video import Video

def wrap_typed(base_file) -> FileObject:
    """Recebe um arquivo base (ex.: GDriveFile) e devolve o wrapper tipado."""
    mime = (getattr(base_file, "mimetype", "") or "").lower()
    name = (getattr(base_file, "name", "") or "").lower()

    # HTML “de verdade”
    if mime.startswith("text/html") or name.endswith(".html") or name.endswith(".htm"):
        return Html(base_file)

    # Google Docs -> trata como HTML (vai ser exportado como HTML no download)
    if mime.startswith("application/vnd.google-apps.document"):
        return Html(base_file)

    # PDF
    if mime.startswith("application/pdf") or name.endswith(".pdf"):
        return Pdf(base_file)

    # Vídeo (bem genérico)
    if mime.startswith("video/"):
        return Video(base_file)

    # fallback
    return FileObject(base_file)
