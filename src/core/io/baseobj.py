# src/core/io/baseobj.py
from __future__ import annotations

class FileObject:
    """Wrapper genérico em cima de um arquivo base (como GDriveFile).
    Exige que o objeto base tenha atributos: id, name, mimetype, e métodos get_raw()/clean().
    """
    def __init__(self, base_file):
        self._f = base_file  # ex.: GDriveFile

    # ---- propriedades comuns ----
    @property
    def id(self) -> str:
        return self._f.id

    @property
    def name(self) -> str:
        return self._f.name

    @property
    def mimetype(self) -> str:
        return getattr(self._f, "mimetype", "") or ""

    # ---- delegações ----
    def get_raw(self, head: int | None = None, permanent: bool = False) -> str:
        return self._f.get_raw(head=head, permanent=permanent)

    def clean(self) -> None:
        return self._f.clean()

    # ---- identificação ----
    def get_type(self) -> str:
        return "file"
