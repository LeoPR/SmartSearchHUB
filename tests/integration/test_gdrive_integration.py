"""
Teste de integração (gated) para Google Drive:
- Só executa se RUN_GDRIVE_INTEGRATION=1.
- Obtém a URI da pasta de teste de uma destas fontes (nessa ordem):
    1) GDRIVE_TEST_FOLDER_URI (ex.: gdrive://<folder-id>)
    2) Storage("sqlite://./config/db.sqlite") se houver entradas
    3) GDRIVE_TEST_FOLDER (apenas o ID; construímos gdrive://<ID>)
- Usa a configuração unificada do projeto: src.providers.config.Config(file="./config/gdrive_auth.json")
  que deve conter as credenciais (service account ou oauth). Para OAuth, o fluxo interativo vai abrir o
  navegador padrão (InstalledAppFlow.run_local_server) quando necessário.

Este teste valida:
- Consegue instanciar Folder via Facade a partir da URI.
- Consegue listar objetos.
- Se houver ao menos um, baixa conteúdo (get_raw) e depois limpa (clean).

Requisitos para execução local:
  export RUN_GDRIVE_INTEGRATION=1
  # Uma das opções de origem da pasta:
  export GDRIVE_TEST_FOLDER_URI="gdrive://<ID>"
  # ou
  preparar ./config/db.sqlite com uma entrada válida (via Storage.bootstrap_from_file, por exemplo)
  # ou
  export GDRIVE_TEST_FOLDER="<ID>"
  # E credenciais:
  - Para service account: apontar no gdrive_auth.json ou usar envs esperadas por esse arquivo.
  - Para OAuth: apontar client_secret/token no gdrive_auth.json.
"""
import os
import pytest

@pytest.mark.integration
def test_gdrive_integration_list_and_download():
    if os.getenv("RUN_GDRIVE_INTEGRATION") != "1":
        pytest.skip("Integration tests disabled (set RUN_GDRIVE_INTEGRATION=1)")

    # Imports locais para evitar custo quando o teste é pulado
    from src.providers.storage import Storage
    from src.providers.config import Config  # Config do projeto (carrega ./config/gdrive_auth.json)
    from src.api.facade import Folder

    # 1) Tenta via env URI
    folder_uri = os.getenv("GDRIVE_TEST_FOLDER_URI")

    # 2) Tenta via Storage, se não veio por env
    if not folder_uri:
        try:
            storage = Storage("sqlite://./config/db.sqlite")
            if len(storage) > 0:
                folder_uri = storage[0]
        except Exception:
            folder_uri = None

    # 3) Tenta via GDRIVE_TEST_FOLDER (ID simples)
    if not folder_uri:
        folder_id = os.getenv("GDRIVE_TEST_FOLDER")
        if folder_id:
            folder_uri = f"gdrive://{folder_id}"

    assert folder_uri, "Defina GDRIVE_TEST_FOLDER_URI ou GDRIVE_TEST_FOLDER, ou prepare config/db.sqlite com uma entrada."

    # Carrega config unificada do projeto
    cfg = Config(file="./config/gdrive_auth.json")

    # Cria Folder via Facade, usando a infra do projeto
    folder = Folder.from_uri(folder_uri, config=cfg, tmp="./tmp", cache="./cache", save="./permanent")

    # Lista objetos
    objs = folder.list()
    assert isinstance(objs, list)

    # Se houver objetos, tenta baixar e ler o início (força download)
    if objs:
        obj = objs[0]
        snippet = obj.get_raw(head={"characters": 128}, permanent=False)
        assert isinstance(snippet, str)
        # Limpa artefatos locais
        obj.clean()