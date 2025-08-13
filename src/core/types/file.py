# src/core/types/file.py
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class FileKind(str, Enum):
    HTML = "html"
    PDF = "pdf"
    TEXT = "text"
    BINARY = "binary"
    UNKNOWN = "unknown"

def guess_kind(mime: str) -> FileKind:
    if not mime:
        return FileKind.UNKNOWN
    if mime.startswith("text/html"):
        return FileKind.HTML
    if mime.startswith("application/pdf"):
        return FileKind.PDF
    if mime.startswith("text/"):
        return FileKind.TEXT
    return FileKind.BINARY

@dataclass
class FileRef:
    id: str
    name: str
    mimetype: str
    modified_time: str | None = None
