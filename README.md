# SmartSearchHUB

Busca modular de arquivos com indexação.

Este projeto é estruturado em camadas:
- src/api: fachada pública (ex.: Folder.from_uri).
- src/core: tipos e abstrações comuns (BaseFile, wrappers de IO).
- src/providers: integrações com provedores (ex.: Google Drive) e utilitários (ex.: Storage/SQLite).
- examples: exemplos mínimos que usam a fachada e provedores.
- tests: testes unitários e de integração (marcados).

Princípios importantes
- Use as abstrações do framework:
  - Para acessar um recurso: Folder.from_uri("gdrive://<id>", config=Config(...)).
  - Para autenticação/configuração do provedor: use a classe Config do provedor (src/providers/google_drive/config.py) carregada via src.providers.config.Config.
  - Não implemente fluxos de autenticação ad-hoc fora de src/providers.
- O fluxo OAuth abre o navegador padrão do sistema (InstalledAppFlow.run_local_server).
- Testes de integração devem ser opcionais (gated por variável de ambiente).

Exemplo rápido (listar pasta do Google Drive)
```bash
# Prepare as credenciais (OAuth ou service account) em ./config/gdrive_auth.json
python examples/list_gdrive_min.py
```

Estrutura (resumo)
- src/api/facade.py: resolve URIs e instancia o provider correto (ex.: GDriveFolder).
- src/providers/google_drive/: Config (autenticação), DriveClient (API), GDriveFolder/GDriveFile (modelo).
- src/core: BaseFile (download/cache), wrappers Html/Pdf/Video via core/io/factory.py.

Testes
- Unitários: não tocam rede; usam mocks/patches.
- Integração: exigem RUN_GDRIVE_INTEGRATION=1 e credenciais válidas. Ver tests/README.md.

Contribuindo
- Siga a arquitetura e use Folder.from_uri + Config.
- Evite chamar SDKs de provedores diretamente em examples/tests; a chamada deve passar pelas classes de src/providers.