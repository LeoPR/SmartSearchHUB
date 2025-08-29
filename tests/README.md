# tests

Estratégia
- Unitários: não acessam rede nem SDKs externos. Use mocks/patches para googleapiclient e para métodos de credenciais.
- Integração: exercem fluxos reais (Drive) e são opcionais. Devem ser marcados com @pytest.mark.integration e executados apenas com RUN_GDRIVE_INTEGRATION=1.

Como rodar
```bash
# Unitários
pytest tests/unit

# Integração (local/ambiente seguro)
export RUN_GDRIVE_INTEGRATION=1
# Fornecer uma pasta de teste por:
#   GDRIVE_TEST_FOLDER_URI="gdrive://<FOLDER_ID>" OR
#   GDRIVE_TEST_FOLDER="<FOLDER_ID>" OR
#   config/db.sqlite (via Storage) contendo uma entrada
pytest -m integration tests/integration
```

Credenciais (integração)
- Service account: referencie no ./config/gdrive_auth.json.
- OAuth: a primeira execução abrirá o navegador padrão do sistema (InstalledAppFlow.run_local_server) e salvará o token no caminho configurado.

Diretriz
- Não chame SDKs externos diretamente nos testes unitários; sempre patche os pontos de integração (ex.: build_credentials, googleapiclient.discovery.build).