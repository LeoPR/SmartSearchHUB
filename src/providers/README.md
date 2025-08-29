# src/providers

Implementações e utilitários de provedores.

- google_drive/
  - Config: autenticação e credenciais (OAuth e service account).
  - DriveClient: API de listagem/consulta.
  - GDriveFolder/GDriveFile: modelos adequados à fachada/core.
- storage.py
  - Persistência simples de URIs de pastas em SQLite para exemplos/testes.
  - Métodos:
    - __getitem__/__len__: acesso a URIs existentes (ex.: "gdrive://...").
    - bootstrap_from_file("./config/bootstrap_folders.json"): popula o DB.
    - reset/close: manutenção.

Diretriz
- Centralize autenticação/credenciais via Config do provider.
- Consumo do provider deve ser via Folder.from_uri.