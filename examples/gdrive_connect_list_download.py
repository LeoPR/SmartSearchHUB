"""
Exemplo melhorado para Google Drive (CLI-friendly, PowerShell-friendly).

Funcionalidade:
- Aceita --folder-uri ou --folder-id (ou lê variáveis de ambiente).
- Aceita --config-file para apontar para um arquivo de configuração (default ./config/gdrive_auth.json).
- Usa a fachada Folder.from_uri + src.providers.config.Config (outra infra do projeto) — NÃO fura a arquitetura.
- Para cada arquivo com mimetype text/html ou text/* ou final .html/.txt faz obj.get_raw(head={'characters':...}) para forçar download
- Não usa Chromium; se for necessário OAuth, Config.build_credentials() usará InstalledAppFlow.run_local_server (abre navegador padrão).

Uso (PowerShell):
  # definir var temporária no PowerShell
  $env:GDRIVE_TEST_FOLDER="1AbCdEfGh"
  python examples/gdrive_connect_list_download.py

  # ou passar por argumento
  python examples/gdrive_connect_list_download.py --folder-id 1AbCdEfGh

Uso (bash):
  export GDRIVE_TEST_FOLDER="1AbCdEfGh"
  python examples/gdrive_connect_list_download.py
"""
from __future__ import annotations
import os
import sys
import argparse

from src.providers.config import Config as ProvidersConfig
from src.api.facade import Folder

def parse_args():
    p = argparse.ArgumentParser(description="Connect to Google Drive, list and download HTML/TXT files (primitive demo).")
    g = p.add_mutually_exclusive_group(required=False)
    g.add_argument("--folder-uri", help="Full URI like gdrive://<FOLDER_ID>")
    g.add_argument("--folder-id", help="Folder ID only; will be converted to gdrive://<ID>")
    p.add_argument("--config-file", default="./config/gdrive_auth.json", help="Path to the project's provider config JSON")
    p.add_argument("--max-files", type=int, default=10, help="Max number of files to download/process")
    p.add_argument("--chars", type=int, default=400, help="Characters to read for snippet")
    return p.parse_args()

def main():
    args = parse_args()

    folder_uri = args.folder_uri
    if not folder_uri and args.folder_id:
        folder_uri = f"gdrive://{args.folder_id}"

    # fallback to env vars (PowerShell / bash)
    if not folder_uri:
        env_uri = os.getenv("GDRIVE_TEST_FOLDER_URI")
        env_id = os.getenv("GDRIVE_TEST_FOLDER")
        if env_uri:
            folder_uri = env_uri
        elif env_id:
            folder_uri = f"gdrive://{env_id}"

    if not folder_uri:
        print("Defina --folder-uri ou --folder-id, ou use env GDRIVE_TEST_FOLDER_URI / GDRIVE_TEST_FOLDER.")
        sys.exit(1)

    # Carrega config do projeto (central)
    cfg = ProvidersConfig(file=args.config_file)

    # Abre via fachada (usa GDriveFolder internamente)
    try:
        folder = Folder.from_uri(folder_uri, config=cfg, tmp="./tmp", cache="./cache", save="./permanent")
    except Exception as e:
        print("Erro ao criar Folder via fachada:", e)
        sys.exit(2)

    print(">>> INFO:", folder.info())

    objs = folder.list()
    print(f"Encontrados {len(objs)} objetos. Processando primeiros {args.max_files} HTML/TXT...")

    processed = 0
    for obj in objs:
        if processed >= args.max_files:
            break
        mim = getattr(obj, "mimetype", "") or ""
        name = getattr(obj, "name", "")
        # heurística simples: html or text or filename endswith .html/.txt
        is_text_like = (
            mim.startswith("text/html") or
            mim.startswith("text/") or
            name.lower().endswith(".html") or
            name.lower().endswith(".txt")
        )
        if is_text_like:
            print(f"[{processed+1}] Baixando: {name} ({mim})")
            try:
                text = obj.get_raw(head={"characters": args.chars}, permanent=False)
                snippet = (text[: args.chars].replace("\n", " ") if isinstance(text, str) else "")
                print("  -> snippet:", snippet[:200])
            except Exception as e:
                print("  Erro ao baixar/ler:", e)
            processed += 1

    print("Concluído.")

if __name__ == "__main__":
    main()