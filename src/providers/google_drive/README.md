# src/providers/google_drive

Integração com Google Drive.

Componentes
- config.py (class Config)
  - auth_method: "oauth" | "service-account"
  - credentials_file: caminho do client_secret.json (OAuth) ou service account JSON
  - token_file: caminho para armazenar token (apenas OAuth)
  - scopes: escopos (default: drive.readonly)
  - build_credentials():
    - Service account: carrega via service_account.Credentials.
    - OAuth: tenta token_file, faz refresh se possível, senão inicia fluxo interativo
      com InstalledAppFlow.run_local_server (abre o navegador padrão do sistema),
      e salva o token em token_file.
- client.py (DriveClient)
  - Encapsula a construção do serviço do Drive (googleapiclient.discovery.build).
  - list_children(folder_id): paginação e retorno de metadados (id, name, mimeType, size).
- folder.py (GDriveFolder)
  - Adapta para a interface do framework:
    - raw_list(): retorna GDriveFile(s).
    - list(): retorna wrappers tipados (Html/Pdf/Video/FileObject) via core/io/factory.wrap_typed.
- file.py (GDriveFile)
  - Extende BaseFile e implementa _download_to (get_media/export_media conforme mimetype).

Como usar (via fachada)
```python
from src.api.facade import Folder
from src.providers.config import Config

cfg = Config(file="./config/gdrive_auth.json")
folder = Folder.from_uri("gdrive://<FOLDER_ID>", config=cfg, tmp="./tmp", cache="./cache")
for obj in folder.list():
    print(obj.name, obj.mimetype, obj.id)
```

Diretrizes
- Não implemente fluxos próprios de OAuth fora deste módulo.
- O fluxo interativo usa o navegador padrão (run_local_server), evitando dependências como Chromium/Playwright.