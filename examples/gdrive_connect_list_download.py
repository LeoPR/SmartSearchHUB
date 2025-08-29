"""
Exemplo mínimo:
- Carrega configuração via src.providers.config.Config(file="./config/gdrive_auth.json")
- Abre uma Folder via Folder.from_uri (usa o framework)
- Lista objetos e, para os tipos HTML/text, faz get_raw() (força download)
- Não usa Chromium; confia em Config.build_credentials() (run_local_server abre navegador padrão)
Config:
- Defina ./config/gdrive_auth.json com auth_method e caminhos adequados
- Defina GDRIVE_TEST_FOLDER_URI="gdrive://<FOLDER_ID>" ou GDRIVE_TEST_FOLDER="<ID>"
"""
from __future__ import annotations
import os
import sys

from src.providers.config import Config as ProvidersConfig
from src.api.facade import Folder

def main():
    # Localiza a URI da pasta (var env ou storage)
    folder_uri = os.getenv("GDRIVE_TEST_FOLDER_URI")
    if not folder_uri:
        fid = os.getenv("GDRIVE_TEST_FOLDER")
        if fid:
            folder_uri = f"gdrive://{fid}"

    if not folder_uri:
        print("Defina GDRIVE_TEST_FOLDER_URI (gdrive://<id>) ou GDRIVE_TEST_FOLDER (id).")
        sys.exit(1)

    # Carrega configuração unificada do projeto (padrão)
    cfg = ProvidersConfig(file="./config/gdrive_auth.json")

    # Abre via fachada (usa GDriveFolder internamente)
    folder = Folder.from_uri(folder_uri, config=cfg, tmp="./tmp", cache="./cache", save="./permanent")

    print(">>> INFO:", folder.info())

    objs = folder.list()
    print(f"Encontrados {len(objs)} objetos. Verificando HTML/TXT e baixando os primeiros 10...")

    count = 0
    for obj in objs:
        if count >= 10:
            break
        mim = getattr(obj, "mimetype", "") or ""
        name = getattr(obj, "name", "")
        # heurística simples: html/text
        if mim.startswith("text/html") or mim.startswith("text/") or name.lower().endswith(".html") or name.lower().endswith(".txt"):
            print(f"Baixando: {name} ({mim})")
            try:
                text = obj.get_raw(head={"characters": 200}, permanent=False)
                snippet = (text[:400].replace("\n", " ") if isinstance(text, str) else "")
                print("  -> snippet:", snippet[:200])
            except Exception as e:
                print("  Erro ao baixar/ler:", e)
            count += 1

if __name__ == "__main__":
    main()