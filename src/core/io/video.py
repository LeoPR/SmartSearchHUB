# src/core/io/video.py
from __future__ import annotations
from .baseobj import FileObject

class Video(FileObject):
    def get_type(self) -> str:
        return "video"
    # futuros: get_metadata(), extract_audio(), etc.
