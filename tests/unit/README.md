# tests/unit

Testes rápidos, isolados de rede/SDKs.

Boas práticas
- Patch nos pontos de borda:
  - src.providers.google_drive.config.Config.build_credentials (retornar objeto fake).
  - googleapiclient.discovery.build (retornar serviço fake com execute() paginado).
- Evite acessar arquivos reais de credenciais/token.

Exemplo (ver test_gdrive_client_pagination.py)
- Verifica paginação de list_children sem tocar na API real.