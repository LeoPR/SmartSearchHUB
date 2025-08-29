# config/

Arquivos de configuração e bootstrap.

Principais itens
- gdrive_auth.json
  - Configuração consumida por src.providers.config.Config para montar a Config específica do Google Drive.
  - Exemplos (ajuste para seu formato real):
```json
{
  "provider": "gdrive",
  "auth_method": "oauth",
  "credentials_file": "./config/credentials/client_secret.json",
  "token_file": "./config/credentials/client_token.json",
  "scopes": ["https://www.googleapis.com/auth/drive.readonly"]
}
```
Ou, para service account:
```json
{
  "provider": "gdrive",
  "auth_method": "service-account",
  "credentials_file": "./config/credentials/service_account.json",
  "scopes": ["https://www.googleapis.com/auth/drive.readonly"]
}
```
- bootstrap_folders.json
  - Usado por providers.Storage.bootstrap_from_file para popular o SQLite com URIs de pastas.
  - Exemplo:
```json
[
  { "driver": "gdrive", "location": "<FOLDER_ID>" }
]
```
- db.sqlite
  - Banco usado por src.providers.storage.Storage; armazena pares (driver, location).
  - Pode ser gerado via bootstrap_from_file.

Observação
- O formato exato de gdrive_auth.json depende de src/providers/config.py. Mantenha os campos mínimos:
  - provider="gdrive"
  - auth_method="oauth"|"service-account"
  - credentials_file e, opcionalmente, token_file (para OAuth).