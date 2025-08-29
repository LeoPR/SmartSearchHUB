# src/api

- facade.py
  - Folder.from_uri(uri, config, tmp="./tmp", cache="./cache", save=None, policy_overrides=None)
  - Suporta URIs no formato "<provider>://<resource_id>".
  - provider gdrive resolve para src.providers.google_drive.folder.GDriveFolder.

Exemplo
```python
from src.api.facade import Folder
from src.providers.config import Config

cfg = Config(file="./config/gdrive_auth.json")
folder = Folder.from_uri("gdrive://<FOLDER_ID>", config=cfg, tmp="./tmp", cache="./cache")
for obj in folder.list():
    print(obj.name, obj.mimetype, obj.id)
```