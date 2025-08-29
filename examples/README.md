# examples

Exemplos focados em demonstrar o uso da fachada e dos provedores do framework, sem “furar” a arquitetura.

Principais scripts
- list_gdrive_min.py
  - Exemplo mínimo: carrega Config (./config/gdrive_auth.json), lê uma URI de pasta do Storage (./config/db.sqlite) e lista arquivos via Folder.from_uri.
- list_gdrive_htmls.py
  - Similar ao anterior, mas demonstra wrappers tipados (Html) e leitura parcial (head).
- list_gdrive_load.py
  - Exemplo simples para exibir/inspecionar a URI carregada do Storage.

Requisitos
- Credenciais configuradas em ./config/gdrive_auth.json (OAuth ou service account).
- Uma URI de pasta válida no ./config/db.sqlite (use providers.Storage.bootstrap_from_file para popular a partir de ./config/bootstrap_folders.json).

Observação
- Evite autenticação ad-hoc aqui: a autenticação deve ser feita via src/providers/google_drive/config.py (classe Config) através de src.providers.config.Config.
- O fluxo OAuth usa o navegador padrão do sistema (run_local_server) quando necessário.