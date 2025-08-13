from __future__ import annotations
from typing import List, Dict, Optional
from googleapiclient.discovery import build

from src.providers.google_drive.config import Config

class DriveClient:
    def __init__(self, config: Config):
        self._config = config
        creds = config.build_credentials()
        # cache_discovery=False evita warning de discovery cache local
        self._svc = build("drive", "v3", credentials=creds, cache_discovery=False)

    def list_children(self, folder_id: str) -> List[Dict]:
        q = f"'{folder_id}' in parents and trashed = false"
        fields = "nextPageToken, files(id,name,mimeType,modifiedTime,size)"
        items: List[Dict] = []
        token: Optional[str] = None
        while True:
            resp = self._svc.files().list(
                q=q,
                fields=fields,
                pageSize=1000,
                pageToken=token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            ).execute()
            items.extend(resp.get("files", []))
            token = resp.get("nextPageToken")
            if not token:
                break
        return items
