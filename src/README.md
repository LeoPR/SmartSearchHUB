# src/

Código-fonte principal (camadas do framework):

- api/
  - Fachada de alto nível. Fornece Folder.from_uri para abrir recursos por URI (ex.: gdrive://<folder-id>).
- core/
  - Abstrações e utilitários independentes de provider:
    - BaseFile (download, cache, limpeza).
    - Tipagem/wrappers de IO (Html, Pdf, Video) e fábrica wrap_typed.
- providers/
  - Implementações por provedor e utilitários de armazenamento:
    - google_drive/: Config (auth), DriveClient (API), GDriveFolder/GDriveFile (modelo).
    - storage.py: leitura/escrita de URIs de pastas em SQLite.

Fluxo típico
User code -> Folder.from_uri -> GDriveFolder -> DriveClient -> API do Google
                           -> GDriveFile (extende BaseFile para download/cache)
                           -> wrap_typed para objetos tipados (Html/Pdf/Video)