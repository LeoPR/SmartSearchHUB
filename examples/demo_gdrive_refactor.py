"""
Demo refatorado que usa src.providers.google_drive.* e GDriveAuthManager.
Mostra como autenticar (interativo se necessário), listar e (opcional) baixar.
Uso mínimo:
  GDRIVE_CREDENTIALS_FILE=./config/credentials/client_secret.json \
  GDRIVE_TOKEN_FILE=./config/credentials/client_token.json \
  GDRIVE_TEST_FOLDER=<ID> \
  python examples/demo_gdrive_refactor.py
"""
from __future__ import annotations
import os
import sys

try:
    from src.providers.google_drive.config import Config as GConfig
    from src.providers.google_drive.auth import GDriveAuthManager
    from src.providers.google_drive.client import DriveClient
except Exception as e:
    print("Erro ao importar módulos do projeto. Verifique se o projeto está no PYTHONPATH e dependências instaladas.")
    print("Detalhe:", e)
    sys.exit(2)

def main():
    folder_id = os.getenv("GDRIVE_TEST_FOLDER")
    if not folder_id:
        print("Defina a variável de ambiente GDRIVE_TEST_FOLDER com o ID da pasta a listar.")
        sys.exit(1)

    cfg = GConfig(
        auth_method=os.getenv("GDRIVE_AUTH_METHOD", "oauth"),
        credentials_file=os.getenv("GDRIVE_CREDENTIALS_FILE", "./config/credentials/client_secret.json"),
        token_file=os.getenv("GDRIVE_TOKEN_FILE", "./config/credentials/client_token.json"),
        scopes=None,  # deixa o default do Config
    )

    auth = GDriveAuthManager(cfg)
    try:
        creds = auth.get_credentials()
    except Exception as e:
        print("Erro ao obter credenciais:", e)
        sys.exit(2)

    # DriveClient internamente chama cfg.build_credentials() — continua compatível.
    client = DriveClient(cfg)
    try:
        items = client.list_children(folder_id)
    except Exception as e:
        print("Erro ao listar folder:", e)
        sys.exit(3)

    print(f"Encontrados {len(items)} arquivos na pasta {folder_id}:")
    for it in items[:50]:
        print(f" - {it.get('name')} ({it.get('id')}) [{it.get('mimeType')}]")

if __name__ == "__main__":
    main()