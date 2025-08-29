# tests/integration

Testes opcionais que exercitam integrações reais (Google Drive).

Como habilitar
```bash
export RUN_GDRIVE_INTEGRATION=1
# informe a pasta de teste:
export GDRIVE_TEST_FOLDER_URI="gdrive://<FOLDER_ID>"
# ou:
export GDRIVE_TEST_FOLDER="<FOLDER_ID>"
# ou prepare config/db.sqlite com uma entrada válida
pytest -m integration
```

Credenciais
- Configuradas em ./config/gdrive_auth.json.
- OAuth abrirá o navegador padrão do sistema na primeira execução para obter o token.

Escopo
- Listagem de arquivos e leitura mínima (get_raw head) para validar download/cache do BaseFile.