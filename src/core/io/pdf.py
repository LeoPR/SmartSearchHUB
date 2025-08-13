# src/core/io/pdf.py
from __future__ import annotations
from .baseobj import FileObject

class Pdf(FileObject):
    def get_type(self) -> str:
        return "pdf"
    # futuros: get_text(), get_images(), etc.
