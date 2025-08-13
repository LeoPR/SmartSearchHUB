# src/core/file.py
from __future__ import annotations
from pathlib import Path
from typing import Optional, Union, Dict

Head = Union[int, Dict[str, int]]

class BaseFile:
    def __init__(self, ref, tmp_dir: Path, cache_dir: Path, save_dir: Optional[Path] = None):
        self.ref = ref          # precisa ter .id, .name, .mimetype
        self.tmp_dir = Path(tmp_dir)
        self.cache_dir = Path(cache_dir)
        self.save_dir = Path(save_dir) if save_dir else None

    def get_raw(self, head: Head | None = None, permanent: bool = False) -> str:
        path = self._ensure_local(permanent=permanent)
        text = path.read_text(encoding="utf-8", errors="ignore")
        if head is None:
            return text
        return self._apply_head(text, head)

    def clean(self) -> None:
        for base in (self.tmp_dir, self.cache_dir, self.save_dir):
            if not base:
                continue
            p = base / self._filename()
            if p.exists():
                p.unlink()

    # ---------- internos ----------
    def _filename(self) -> str:
        # usa ref direto para evitar conflito com dataclass
        return f"{getattr(self.ref, 'id', '')}__{getattr(self.ref, 'name', '')}"

    def _ensure_local(self, permanent: bool) -> Path:
        target = (self.save_dir if permanent and self.save_dir else self.cache_dir)
        target.mkdir(parents=True, exist_ok=True)
        local = target / self._filename()
        if not local.exists():
            self.tmp_dir.mkdir(parents=True, exist_ok=True)
            tmp_path = self.tmp_dir / self._filename()
            self._download_to(tmp_path)
            tmp_path.replace(local)
        return local

    def _download_to(self, dest: Path) -> None:
        raise NotImplementedError

    @staticmethod
    def _apply_head(text: str, head: Head) -> str:
        if isinstance(head, int):
            return "".join(text.splitlines(keepends=True)[:head])
        lines = head.get("lines")
        chars = head.get("characters")
        if lines is None and chars is None:
            return text
        if lines is not None:
            chunks = text.splitlines(keepends=True)[: max(0, int(lines))]
            if chars is not None:
                m = max(0, int(chars))
                chunks = [c[:m] for c in chunks]
            return "".join(chunks)
        return text[: max(0, int(chars))]
