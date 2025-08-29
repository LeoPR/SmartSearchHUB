"""
Teste de integração (gated). Só roda se RUN_GDRIVE_INTEGRATION=1.
Exige configuração de ambiente:
  - GOOGLE_APPLICATION_CREDENTIALS (service account) OU
  - GDRIVE_CREDENTIALS_FILE / GDRIVE_TOKEN_FILE para OAuth interativo local
  - GDRIVE_TEST_FOLDER com ID da pasta de teste

Este teste não é executado por padrão no CI.