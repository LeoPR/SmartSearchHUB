# src/providers/google_drive/folder.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict

from src.providers.google_drive.config import Config
from src.providers.google_drive.client import DriveClient
from src.providers.google_drive.file import GDriveFile

@dataclass
class GDriveFolder:
    uri: str
    resource_id: str
    config: Config
    tmp_dir: Path
    cache_dir: Path
    save_dir: Optional[Path] = None
    policy_overrides: dict = None

    def __post_init__(self):
        self.client = DriveClient(self.config)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if self.save_dir:
            self.save_dir.mkdir(parents=True, exist_ok=True)

    def info(self) -> dict:
        return {"provider": "gdrive", "resource_id": self.resource_id}

    def _map_item(self, it: Dict) -> Dict:
        return {
            "id": it.get("id"),
            "name": it.get("name"),
            "mimetype": it.get("mimeType"),
            "size": int(it["size"]) if it.get("size") is not None else None,
        }

    # --- NOVO: lista “bruta” (objetos do provider) ---
    def raw_list(self) -> List[GDriveFile]:
        items = self.client.list_children(self.resource_id)
        return [GDriveFile(folder=self, **self._map_item(it)) for it in items]

    # --- Alterado: lista tipada (wrappers do CORE) ---
    def list(self) -> List[object]:
        from src.core.io.factory import wrap_typed  # lazy import p/ evitar ciclos
        return [wrap_typed(f) for f in self.raw_list()]
