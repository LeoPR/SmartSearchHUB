# Examples - SmartSearchHUB

Este diretório contém **examples práticos** para demonstrar as funcionalidades do SmartSearchHUB, um framework Python modular para busca e indexação de arquivos.

## 📋 **Resumo para IA**

O SmartSearchHUB é um framework que permite conectar a diferentes provedores (Google Drive, URLs, etc.) para:
- **Autenticar** automaticamente (OAuth, Service Account)
- **Listar** conteúdo de pastas/sites
- **Extrair** texto estruturado de HTML, documentos, etc.
- **Processar** em lote com cache inteligente

Os examples demonstram casos de uso reais, desde autenticação básica até extração avançada de conteúdo.

---

## 🚀 **Quick Start**

### **1. Setup Inicial**
```powershell
# Criar arquivos de configuração
python -m examples --setup
```

### **2. Configurar Google Drive**
```powershell
# 1. Baixe credenciais do Google Console
# 2. Salve em ./config/credentials/
# 3. Configure ./config/gdrive_auth.json
```

### **3. Executar Examples**
```powershell
# Definir pasta de teste
$env:GDRIVE_TEST_FOLDER="1AbCdEf..."

# Examples específicos
python -m examples gdrive 01    # Autenticação
python -m examples gdrive 02    # Listagem
python -m examples gdrive 03    # Extração de conteúdo

# Todos em sequência  
python -m examples gdrive
```

---

## 📚 **Examples Implementados**

| Example | Funcionalidade | Requer Pasta | Status |
|---------|----------------|--------------|--------|
| **01_auth_test** | Teste de autenticação | ❌ | ✅ |
| **02_list_basic** | Listagem de arquivos | ✅ | ✅ |
| **03_extract_html** | Extração de conteúdo | ✅ | ✅ |
| **04_recursive** | Navegação recursiva | ✅ | 🚧 |
| **05_batch_process** | Processamento em lote | ✅ | 🚧 |

### **🔐 01_auth_test.py - Teste de Autenticação**
```powershell
python -m examples.gdrive 01
```
- Verifica autenticação OAuth/Service Account
- Não requer pasta específica
- Testa detecção automática de credenciais

### **📁 02_list_basic.py - Listagem Básica**
```powershell
$env:GDRIVE_TEST_FOLDER="folder_id"
python -m examples.gdrive 02
```
- Lista arquivos sem downloads
- Mostra estatísticas por tipo MIME
- Configurável: `GDRIVE_MAX_FILES=10`

### **📄 03_extract_html.py - Extração de Conteúdo ⭐**
```powershell
$env:GDRIVE_TEST_FOLDER="folder_id"
python -m examples.gdrive 03
```
- Filtra conteúdo de texto/HTML automaticamente
- Extrai dados brutos + texto limpo
- Analisa links (internos vs externos)
- Mostra estatísticas (palavras, linhas)

**Configurações**:
- `GDRIVE_MAX_FILES=5` - Arquivos a processar
- `GDRIVE_PREVIEW_LENGTH=300` - Tamanho do preview  
- `GDRIVE_EXTRACT_LINKS=true` - Extrair links

---

## 🛠️ **Componentes Principais**

### **🔐 AuthManager** 
Coordenador de autenticação que:
- Detecta credenciais automaticamente
- Suporta OAuth + Service Account
- Controla interatividade (`interactive=True/False`)
- Avisa antes de abrir navegador

### **📄 ContentExtractor**
Extrator de conteúdo que:
- Filtra HTML, Google Docs, texto
- Remove tags HTML → texto limpo
- Extrai links e metadados
- Funciona com diferentes fontes

---

## 🎯 **Casos de Uso**

### **Exploração Rápida**
```powershell
$env:GDRIVE_TEST_FOLDER="abc123"
python -m examples gdrive 02 03  # Lista + extrai
```

### **Análise Detalhada**  
```powershell
$env:GDRIVE_MAX_FILES="10"
$env:GDRIVE_PREVIEW_LENGTH="500"
python -m examples gdrive 03
```

### **Modo Batch (Futuro)**
```powershell
python -m examples gdrive 05  # Processa pasta inteira
```

---

## 🔧 **Configuração**

### **OAuth (Desenvolvimento)**
`./config/gdrive_auth.json`:
```json
{
  "auth_method": "oauth",
  "credentials_file": "./config/credentials/client_secret.json",
  "token_file": "./config/credentials/client_token.json"
}
```

### **Service Account (Produção)**
```json
{
  "auth_method": "service_account",
  "credentials_file": "./config/credentials/sa-service-account.json"
}
```

---

## 🐛 **Troubleshooting**

### **❌ "Variável não definida"**
```powershell
# PowerShell - com aspas!
$env:GDRIVE_TEST_FOLDER="folder_id"
```

### **❌ "Credenciais não encontradas"**
```powershell
python -m examples --setup           # Criar templates
python -m examples.common test-detection  # Verificar detecção
```

### **❌ "Module not found"**
- Execute da raiz do projeto
- Ative ambiente virtual

---

## 📊 **Variáveis de Ambiente**

| Variável | Uso | Default | Exemplos |
|----------|-----|---------|----------|
| `GDRIVE_TEST_FOLDER` | ID da pasta | - | `"1AbCdEf..."` |
| `GDRIVE_MAX_FILES` | Limite de arquivos | `10` | `"5"`, `"20"` |
| `GDRIVE_PREVIEW_LENGTH` | Preview chars | `300` | `"500"` |
| `GDRIVE_EXTRACT_LINKS` | Extrair links | `true` | `"false"` |
| `GDRIVE_INTERACTIVE` | Modo interativo | `true` | `"false"` |
| `DEBUG` | Debug detalhado | - | `"1"` |

---

## 🎯 **Comandos Essenciais**

```powershell
# Setup inicial
python -m examples --setup

# Listar examples
python -m examples gdrive --list

# Teste rápido
$env:GDRIVE_TEST_FOLDER="folder_id"
python -m examples gdrive 01 02 03

# Debug
$env:DEBUG="1"
python -m examples gdrive 03
```

---

**🚀 Examples práticos para explorar todo o potencial do SmartSearchHUB!**

Para documentação completa, veja os comentários em cada arquivo de example.


# examples antigos, devem ser removidos depois

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