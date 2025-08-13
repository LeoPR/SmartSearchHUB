from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TYPE_CHECKING
import io

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from src.core.file import BaseFile
from src.core.types.file import FileRef
from src.providers.google_drive.config import Config

if TYPE_CHECKING:
    # só para type hints; não roda em tempo de execução
    from .folder import GDriveFolder

@dataclass
class GDriveFile(BaseFile):
    id: str
    name: str
    mimetype: str
    size: Optional[int] = None
    folder: "GDriveFolder" | None = None

    def __post_init__(self):
        ref = FileRef(
            id=self.id,
            name=self.name,
            mimetype=self.mimetype,
            modified_time=None,
        )
        super().__init__(
            ref=ref,
            tmp_dir=self.folder.tmp_dir if self.folder else Path("./tmp"),
            cache_dir=self.folder.cache_dir if self.folder else Path("./cache"),
            save_dir=self.folder.save_dir if self.folder else None,
        )
        self._cfg: Config = self.folder.config if self.folder else Config()

    def _download_to(self, dest: Path) -> None:
        creds = self._cfg.build_credentials()
        service = build("drive", "v3", credentials=creds)

        is_google_doc = (self.mimetype or "").startswith("application/vnd.google-apps.")
        fh = io.FileIO(dest, "wb")
        try:
            if is_google_doc:
                export_mime = "text/html" if "document" in self.mimetype else "text/plain"
                request = service.files().export_media(fileId=self.id, mimeType=export_mime)
            else:
                request = service.files().get_media(fileId=self.id)

            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        finally:
            fh.close()
