#!/usr/bin/env python3
"""
Demo: lista arquivos de uma pasta do Google Drive.

Suporta autenticação via:
- Service Account (preferencial). Usa entry.auth.file ou env var (default GOOGLE_APPLICATION_CREDENTIALS).
- OAuth (interativo). Usa entry.auth.credentials_file + entry.auth.token_file.

Execute:
  python -m examples.demo_gdrive
"""
import os
import sys

# Importa utils primeiro para inserir src/ no sys.path
from examples.utils import load_bootstrap, filter_entries
from examples.utils_auth import load_auth_for_entry, get_gdrive_credentials, DEFAULT_DRIVE_SCOPES

try:
    from googleapiclient.discovery import build
except Exception:
    build = None  # veremos em runtime


def list_drive_folder(folder_id: str, creds):
    service = build("drive", "v3", credentials=creds)
    q = f"'{folder_id}' in parents and trashed = false"
    page_token = None
    files = []
    while True:
        resp = (
            service.files()
            .list(
                q=q,
                spaces="drive",
                fields="nextPageToken, files(id, name, mimeType, size)",
                pageToken=page_token,
            )
            .execute()
        )
        files.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return files


def main():
    if build is None:
        print("Dependências Google ausentes. Instale:")
        print("  pip install google-api-python-client google-auth google-auth-oauthlib")
        sys.exit(2)

    try:
        entries = load_bootstrap()
    except FileNotFoundError as e:
        print("Erro:", e)
        sys.exit(1)

    g_entries = filter_entries(entries, driver="gdrive")
    if not g_entries:
        print("Nenhuma entrada 'gdrive' em config/bootstrap_folders.json")
        return

    for entry in g_entries:
        folder_id = entry.get("location")
        if not folder_id:
            continue

        # Lê auth do bootstrap
        auth_info = load_auth_for_entry(entry)

        # Fallback prático: se method=none e houver env GOOGLE_APPLICATION_CREDENTIALS, usa service_account
        if auth_info.get("method") == "none":
            sa_env = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if sa_env:
                auth_info = {
                    "method": "service_account",
                    "file": sa_env,
                    "env_var": "GOOGLE_APPLICATION_CREDENTIALS",
                    "scopes": DEFAULT_DRIVE_SCOPES,
                }

        print(f"\n--- Listando Drive folder: {folder_id}")
        try:
            creds = get_gdrive_credentials(auth_info)
        except Exception as e:
            print("Erro de autenticação/configuração:", e)
            continue

        try:
            files = list_drive_folder(folder_id, creds)
        except Exception as e:
            print("Erro ao listar folder:", e)
            continue

        print(f"Arquivos encontrados: {len(files)}")
        for f in files[:30]:
            print(f" - {f.get('name')} ({f.get('id')}) [{f.get('mimeType')}]")

if __name__ == "__main__":
    main()