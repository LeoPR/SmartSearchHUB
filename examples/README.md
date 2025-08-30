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
| **03_extract_html** | Extração de conteúdo HTML | ✅ | ✅ |
| **04_extract_pdf** | Extração de conteúdo PDF | ✅ | ✅ |
| **05_batch_process** | Processamento em lote | ✅ | 🚧 |

### **📄 04_extract_pdf.py - Extração de PDF ⭐**
```powershell
$env:GDRIVE_TEST_FOLDER="folder_id"
python -m examples.gdrive 04
```
- Detecta automaticamente bibliotecas PDF disponíveis
- Extrai texto, metadados e estatísticas
- Análise página por página
- Suporte a PDFs baseados em texto e imagem
- Relatório detalhado de tipos de PDF

**Configurações**:
- `GDRIVE_PDF_MAX_FILES=3` - PDFs a processar
- `GDRIVE_PDF_MAX_PAGES=5` - Páginas por PDF
- `GDRIVE_PDF_PREVIEW_LENGTH=200` - Tamanho do preview
- `GDRIVE_PDF_EXTRACT_METADATA=true` - Extrair metadados

**Bibliotecas Suportadas**:
- PyMuPDF (recomendado): `pip install PyMuPDF`
- pdfplumber: `pip install pdfplumber` 
- PyPDF2: `pip install PyPDF2`

## 🎯 **Casos de Uso** (ATUALIZADO)

### **Exploração Completa**
```powershell
$env:GDRIVE_TEST_FOLDER="abc123"
python -m examples gdrive 02 03 04  # Lista + HTML + PDF
```

### **Análise Específica de PDF**  
```powershell
$env:GDRIVE_PDF_MAX_FILES="5"
$env:GDRIVE_PDF_MAX_PAGES="10"
python -m examples gdrive 04
```

### **Comparação HTML vs PDF**
```powershell
# Extrair ambos os tipos
python -m examples gdrive 03 04
```

## 📊 **Variáveis de Ambiente** (ATUALIZADAS)

| Variável | Uso | Default | Exemplos |
|----------|-----|---------|----------|
| `GDRIVE_TEST_FOLDER` | ID da pasta | - | `"1AbCdEf..."` |
| `GDRIVE_MAX_FILES` | Limite de arquivos (geral) | `10` | `"5"`, `"20"` |
| `GDRIVE_PDF_MAX_FILES` | Limite PDFs específico | `3` | `"5"`, `"10"` |
| `GDRIVE_PDF_MAX_PAGES` | Páginas por PDF | `5` | `"10"`, `"all"` |
| `GDRIVE_PDF_PREVIEW_LENGTH` | Preview por página | `200` | `"300"`, `"500"` |
| `GDRIVE_PDF_EXTRACT_METADATA` | Extrair metadados PDF | `true` | `"false"` |
| `GDRIVE_PREVIEW_LENGTH` | Preview HTML (geral) | `300` | `"500"` |
| `GDRIVE_EXTRACT_LINKS` | Extrair links HTML | `true` | `"false"` |
| `GDRIVE_INTERACTIVE` | Modo interativo | `true` | `"false"` |
| `DEBUG` | Debug detalhado | - | `"1"` |

## 🎯 **Comandos Essenciais** (ATUALIZADOS)

```powershell
# Setup inicial
python -m examples --setup

# Listar examples
python -m examples gdrive --list

# Teste completo (todos os examples)
$env:GDRIVE_TEST_FOLDER="folder_id"
python -m examples gdrive

# Examples específicos
python -m examples gdrive 01        # Só autenticação
python -m examples gdrive 02 03     # HTML + listagem
python -m examples gdrive 04        # Só PDF
python -m examples gdrive 03 04     # HTML + PDF

# Debug específico
$env:DEBUG="1"
python -m examples gdrive 04
```

## 🛠️ **Dependências Opcionais**

### **Para melhor suporte PDF:**
```powershell
# Opção 1: PyMuPDF (recomendado - mais rápido)
pip install PyMuPDF

# Opção 2: pdfplumber (bom para tabelas)
pip install pdfplumber

# Opção 3: PyPDF2 (básico, sempre funciona)  
pip install PyPDF2
```

### **Verificar bibliotecas instaladas:**
```powershell
python -c "
try:
    import fitz; print('✅ PyMuPDF instalado')
except: print('❌ PyMuPDF não encontrado')
    
try:  
    import pdfplumber; print('✅ pdfplumber instalado')
except: print('❌ pdfplumber não encontrado')
    
try:
    import PyPDF2; print('✅ PyPDF2 instalado') 
except: print('❌ PyPDF2 não encontrado')
"
```

## 📊 **Exemplo de Saída - PDF**

```
📄 EXTRAÇÃO DE CONTEÚDO PDF - GOOGLE DRIVE
======================================================================
📂 Pasta: 1AbCdEfGhIjKlMnOp
📊 Máximo de arquivos: 3
📊 Máximo de páginas por PDF: 5
🔍 Extrair metadados: ✅ Sim

🔍 Verificando bibliotecas PDF...
✅ Biblioteca PDF detectada: PyMuPDF (recomendado)

🔗 Conectando à pasta...
📋 Listando arquivos...

📊 Arquivos encontrados:
   Total na pasta: 15
   Arquivos PDF: 2
   A processar: 2

🚀 Processando PDFs...
======================================================================

[1/2] 📄 Manual_Usuario.pdf
   🔍 Extraindo metadados...
   📊 Informações básicas:
      Título: Manual do Usuário - Sistema XYZ
      Autor: Equipe Técnica
      Páginas: 8
      Tipo PDF: text_based
   📝 Extraindo texto...
   📊 Estatísticas do texto:
      Caracteres: 12,450
      Palavras: 2,180
      Linhas: 245
   📋 Análise por páginas:
      Páginas processadas: 5
        Página 1: 380 palavras
        Página 2: 425 palavras
        Página 3: 390 palavras
   📝 Preview do conteúdo:
      MANUAL DO USUÁRIO
      Sistema de Gerenciamento XYZ
      Versão 2.1 - Março 2024...

[2/2] 📄 Relatorio_Vendas.pdf
   🔍 Extraindo metadados...
   📊 Informações básicas:
      Páginas: 3
      Tipo PDF: mixed
   📝 Extraindo texto...
   📊 Estatísticas do texto:
      Caracteres: 5,820
      Palavras: 940
      Linhas: 88
   📋 Análise por páginas:
      Páginas processadas: 3
        Página 1: 320 palavras
        Página 2: 280 palavras
        Página 3: 340 palavras
   📝 Preview do conteúdo:
      RELATÓRIO DE VENDAS
      Período: Janeiro - Março 2024
      Total Vendido: R$ 145.680...

======================================================================
📊 RESUMO FINAL - EXTRAÇÃO DE PDFs
======================================================================
✅ PDFs processados: 2/2
📄 Total de páginas analisadas: 8
📝 Total de palavras: 3,120
📊 Média de palavras por PDF: 1,560
📊 Média de palavras por página: 390

📈 Distribuição por tipo de PDF:
   Text Based: 1 PDF(s)
   Mixed: 1 PDF(s)

🎉 EXTRAÇÃO DE PDFs CONCLUÍDA COM SUCESSO!
```

## 🔧 **Troubleshooting PDF**

### **❌ "Nenhuma biblioteca PDF detectada"**
```powershell
# Instalar pelo menos uma biblioteca
pip install PyMuPDF  # Mais rápida e completa

# Verificar instalação
python -c "import fitz; print('PyMuPDF OK')"
```

### **❌ "Nenhum texto extraído"**
- PDF pode ser baseado em imagens (precisa OCR)
- PDF pode estar criptografado/protegido
- Tente biblioteca diferente:
```powershell
pip install pdfplumber  # Alternativa
```

### **❌ "Erro de memória com PDFs grandes"**
```powershell
# Limite páginas processadas
$env:GDRIVE_PDF_MAX_PAGES="3"
python -m examples gdrive 04
```

## 💡 **Dicas de Uso**

### **Para análise rápida:**
```powershell
$env:GDRIVE_PDF_MAX_FILES="1"
$env:GDRIVE_PDF_MAX_PAGES="2" 
python -m examples gdrive 04
```

### **Para análise completa:**
```powershell
$env:GDRIVE_PDF_MAX_FILES="10"
$env:GDRIVE_PDF_MAX_PAGES="all"
$env:GDRIVE_PDF_EXTRACT_METADATA="true"
python -m examples gdrive 04
```

### **Para comparar tipos de arquivo:**
```powershell
# Processar HTML e PDF na mesma sessão
python -m examples gdrive 03 04
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