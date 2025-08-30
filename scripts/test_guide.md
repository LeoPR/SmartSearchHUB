# 🧪 Guia de Teste dos Examples - SmartSearchHUB

## ✅ **Estado Atual - 100% Implementado**

**Implementado e Pronto para Teste:**
- ✅ AuthManager funcional (OAuth validado) 
- ✅ ContentExtractor implementado
- ✅ Examples 01, 02 e 03 completos
- ✅ Estrutura modular completa
- ✅ Documentação completa

## 🎯 **Próximos Passos Imediatos**

### **Fase 1: Configuração de Credenciais**

1. **Baixe credenciais do Google Console:**
   - Vá para [Google Cloud Console](https://console.cloud.google.com/)
   - Crie um projeto ou use existente
   - Ative a API do Google Drive
   - Crie credenciais OAuth 2.0 (aplicativo desktop)
   - Baixe o arquivo `client_secret_XXXXX.json`

2. **Configure o projeto:**
   ```powershell
   # Clone/navegue até o projeto
   cd SmartSearchHUB
   
   # Crie estrutura de credenciais
   mkdir -p config/credentials
   
   # Copie suas credenciais
   cp "Downloads/client_secret_XXXXX.json" "config/credentials/"
   
   # Crie configuração base
   python -m examples --setup
   ```

3. **Ajuste configuração:**
   Edite `./config/gdrive_auth.json`:
   ```json
   {
     "auth_method": "oauth",
     "credentials_file": "./config/credentials/client_secret_XXXXX.json",
     "token_file": "./config/credentials/client_token.json",
     "scopes": ["https://www.googleapis.com/auth/drive.readonly"]
   }
   ```

### **Fase 2: Preparação da Pasta de Teste**

1. **Crie pasta no Google Drive:**
   - Acesse [drive.google.com](https://drive.google.com)
   - Crie uma pasta "SmartSearchHUB Test"
   - Adicione alguns arquivos:
     - Documentos HTML ou Google Docs
     - Arquivos de texto (.txt)
     - Documentos variados

2. **Obtenha ID da pasta:**
   - Abra a pasta no navegador
   - URL será: `https://drive.google.com/drive/folders/FOLDER_ID`
   - Copie o `FOLDER_ID`

### **Fase 3: Testes Sequenciais**

#### **Teste 1: Autenticação (01_auth_test.py)**
```powershell
# Teste básico de autenticação
python -m examples.gdrive 01

# Resultado esperado:
# ✅ Autenticação bem-sucedida!
# ✅ Credenciais válidas e prontas para uso!
```

#### **Teste 2: Listagem (02_list_basic.py)**
```powershell
# Defina pasta de teste
$env:GDRIVE_TEST_FOLDER="FOLDER_ID_AQUI"

# Execute listagem
python -m examples.gdrive 02

# Resultado esperado:
# 📊 Encontrados X arquivo(s), exibindo primeiros 10
# 📈 Estatísticas por tipo MIME
```

#### **Teste 3: Extração (03_extract_html.py)**
```powershell
# Configure extração avançada
$env:GDRIVE_TEST_FOLDER="FOLDER_ID_AQUI"
$env:GDRIVE_MAX_FILES="5"
$env:GDRIVE_EXTRACT_LINKS="true"

# Execute extração
python -m examples.gdrive 03

# Resultado esperado:
# 📄 Arquivos de texto/HTML processados
# 📊 Estatísticas detalhadas (palavras, links)
# 📝 Preview do conteúdo
```

#### **Teste 4: Execução em Lote**
```powershell
# Execute todos os examples em sequência
$env:GDRIVE_TEST_FOLDER="FOLDER_ID_AQUI"
python -m examples.gdrive

# Resultado esperado:
# [1/3] Example 01 ✅ executado com sucesso
# [2/3] Example 02 ✅ executado com sucesso  
# [3/3] Example 03 ✅ executado com sucesso
# ✅ Sucessos: 3/3
```

## 🐛 **Troubleshooting**

### **Problemas Comuns:**

#### **❌ "Module not found"**
```powershell
# Execute da raiz do projeto
cd SmartSearchHUB
python -m examples.gdrive 01

# Se usar venv:
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

#### **❌ "GDRIVE_TEST_FOLDER não definida"**
```powershell
# PowerShell - com aspas!
$env:GDRIVE_TEST_FOLDER="1AbCdEfGh12345"

# Ou export permanente
[Environment]::SetEnvironmentVariable("GDRIVE_TEST_FOLDER", "1AbCdEfGh12345", "User")
```

#### **❌ "Credenciais não encontradas"**
```powershell
# Verificar detecção
python -m examples.common test-detection

# Recriar templates
python -m examples --setup
```

#### **❌ Erro OAuth no navegador**
- Certifique-se que a API do Drive está ativada
- Verifique se o redirect URI está configurado
- Tente método Service Account se necessário

### **Debug Avançado:**
```powershell
# Ativa logs detalhados
$env:DEBUG="1"
python -m examples.gdrive 03

# Testa AuthManager isoladamente
python -m examples.common test-detection
```

## 📊 **Validação dos Resultados**

### **Example 01 - Sucesso se:**
- ✅ AuthManager inicializado
- ✅ Configurações detectadas
- ✅ Credenciais válidas
- ✅ "TESTE DE AUTENTICAÇÃO CONCLUÍDO"

### **Example 02 - Sucesso se:**
- ✅ Lista arquivos da pasta
- ✅ Mostra estatísticas por MIME
- ✅ Informações corretas dos arquivos

### **Example 03 - Sucesso se:**
- ✅ Filtra arquivos processáveis
- ✅ Extrai texto limpo de HTML/Docs
- ✅ Analisa links (se habilitado)
- ✅ Mostra estatísticas de palavras
- ✅ Preview do conteúdo

### **Execução em Lote - Sucesso se:**
- ✅ Executa todos em sequência
- ✅ Relatório final: "Sucessos: 3/3"
- ✅ Sem falhas críticas

## 🚀 **Após Validação Bem-Sucedida**

Com os testes passando, estaremos prontos para:

### **Fase 2: Examples Avançados**
- ✅ 04_recursive_folders.py - Navegação recursiva
- ✅ 05_batch_process.py - Processamento em lote otimizado
- ✅ Integração com sistema de cache inteligente

### **Fase 3: Expansão**
- ✅ examples/url/ - Suporte a URLs com autenticação
- ✅ Navegação recursiva em websites
- ✅ Abstração unificada GDrive/URL

### **Fase 4: Migração Final**
- ✅ Migrar examples antigos para nova estrutura
- ✅ Deprecar arquivos legados
- ✅ Documentação final completa

## 📝 **Comandos de Teste Rápido**

```powershell
# Setup inicial completo
python -m examples --setup

# Teste de autenticação
python -m examples.gdrive 01

# Configurar pasta de teste
$env:GDRIVE_TEST_FOLDER="SEU_FOLDER_ID"

# Teste completo
python -m examples.gdrive

# Debug se necessário
$env:DEBUG="1"
python -m examples.gdrive 03
```

## 🎯 **Critérios de Sucesso**

**✅ Fase 1 Concluída se:**
1. Example 01 autentica com sucesso
2. Example 02 lista arquivos corretamente
3. Example 03 extrai conteúdo e links
4. Execução em lote funciona sem erros
5. Documentação está clara e completa

**🎉 Com esses testes passando, o refactor dos Examples estará 100% concluído e validado!**