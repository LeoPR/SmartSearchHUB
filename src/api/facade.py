from __future__ import annotations
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from src.providers.google_drive.config import Config

def _parse_uri(uri: str) -> Tuple[str, str]:
    if "://" not in uri:
        raise ValueError("URI deve ser <provider>://<resource_id>")
    provider, rest = uri.split("://", 1)
    return provider.lower(), rest

class Folder:
    @staticmethod
    def from_uri(
        uri: str,
        config: Config,
        tmp: str = "./tmp",
        cache: str = "./cache",
        save: Optional[str] = None,
        policy_overrides: Optional[Dict[str, Any]] = None,
    ):
        provider, resource = _parse_uri(uri)
        if provider in ("gdrive", "googledrive", "google-drive"):
            # lazy import evita ciclos
            from src.providers.google_drive.folder import GDriveFolder
            return GDriveFolder(
                uri=uri,
                resource_id=resource,
                config=config,
                tmp_dir=Path(tmp),
                cache_dir=Path(cache),
                save_dir=Path(save) if save else None,
                policy_overrides=policy_overrides or {},
            )
        raise NotImplementedError(f"Provider não suportado: {provider}")
