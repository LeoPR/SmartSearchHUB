# Configuração de Autenticação

## Google Drive

1. **OAuth (Recomendado para desenvolvimento)**:
   - Baixe `client_secret.json` do Google Console
   - Salve em `./config/credentials/`
   - Copie `gdrive_auth.example.json` para `gdrive_auth.json`
   - Ajuste o caminho do `credentials_file`

2. **Service Account (Para produção)**:
   - Baixe JSON da service account
   - Salve em `./config/credentials/sa-service-account.json`
   - Configure `gdrive_auth.json` com `auth_method: "service_account"`

## Exemplo de uso:

```python
from examples.common.auth_manager import AuthManager

auth = AuthManager(interactive=True)
config = auth.get_gdrive_config()
```
