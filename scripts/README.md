# 🛠️ Scripts de Automação - SmartSearchHUB

Scripts utilitários para desenvolvimento, teste e validação do projeto.

## 📋 **Scripts Disponíveis**

### **🧪 validate_examples.py**
Validador automático de examples - executa todos os examples em sequência e valida resultados.

#### **Uso Básico:**
```bash
# Validação completa
python scripts/validate_examples.py

# Com pasta específica
python scripts/validate_examples.py --folder-id 1AbCdEfGhIjKlMnOpQr

# Pular autenticação (se já configurada)
python scripts/validate_examples.py --skip-auth

# Salvar relatório detalhado
python scripts/validate_examples.py --save-report validation.txt
```

#### **O que Valida:**
- ✅ Pré-requisitos (estrutura de arquivos)
- ✅ Example 01: Autenticação OAuth/Service Account
- ✅ Example 02: Listagem básica de arquivos
- ✅ Example 03: Extração de conteúdo HTML/texto
- ✅ Códigos de retorno e mensagens de sucesso
- ✅ Performance (tempo de execução)

#### **Configurações de Teste:**
- `GDRIVE_MAX_FILES=3` - Poucos arquivos para teste rápido
- `GDRIVE_PREVIEW_LENGTH=100` - Preview curto
- Timeout de 60s por teste

#### **Exemplo de Saída:**
```
🚀 VALIDAÇÃO AUTOMÁTICA DOS EXAMPLES
============================================================
🔍 Verificando pré-requisitos...
✅ Pré-requisitos verificados
⚙️ Configurando ambiente de teste...
📂 Pasta de teste: 1AbCdEfGhIjKlMnOpQr

🧪 Executando: Teste de Autenticação
----------------------------------------
✅ Teste de Autenticação executado com sucesso (2.1s)
   ✅ Autenticação validada

🧪 Executando: Listagem Básica
----------------------------------------
✅ Listagem Básica executado com sucesso (3.5s)
   ✅ Listagem validada

🧪 Executando: Extração de Conteúdo
----------------------------------------
✅ Extração de Conteúdo executado com sucesso (5.2s)
   ✅ Extração validada

============================================================
📊 RELATÓRIO FINAL DE VALIDAÇÃO
============================================================
✅ Sucessos: 3/3
❌ Falhas: 0

🎉 Tests bem-sucedidos:
   ✅ Teste de Autenticação (2.1s)
   ✅ Listagem Básica (3.5s)
   ✅ Extração de Conteúdo (5.2s)

🎉 VALIDAÇÃO COMPLETA: TODOS OS EXAMPLES FUNCIONANDO!
✅ O refactor dos Examples foi bem-sucedido
🚀 Pronto para partir para Fase 2: Examples Avançados
```

## 🎯 **Casos de Uso**

### **Desenvolvimento Local**
```bash
# Teste rápido após mudanças
python scripts/validate_examples.py --folder-id SUA_PASTA_ID

# Validação completa para PR
python scripts/validate_examples.py --save-report pr_validation.txt
```

### **CI/CD Pipeline**
```yaml
# GitHub Actions example
- name: Validate Examples
  run: |
    python scripts/validate_examples.py --skip-auth
  env:
    GDRIVE_TEST_FOLDER: ${{ secrets.TEST_FOLDER_ID }}
```

### **Debug de Problemas**
```bash
# Se algum teste falhar, execute individualmente:
python -m examples.gdrive 01  # Autenticação
python -m examples.gdrive 02  # Listagem  
python -m examples.gdrive 03  # Extração

# Com debug habilitado:
DEBUG=1 python -m examples.gdrive 03
```

## 🔧 **Extensibilidade**

### **Adicionando Novos Testes**
Para validar novos examples, modifique o array `tests` em `validate_examples.py`:

```python
tests = [
    ("01_auth_test", "Teste de Autenticação", []),
    ("02_list_basic", "Listagem Básica", ["GDRIVE_TEST_FOLDER"]),
    ("03_extract_html", "Extração de Conteúdo", ["GDRIVE_TEST_FOLDER"]),
    ("04_recursive", "Navegação Recursiva", ["GDRIVE_TEST_FOLDER"]),  # Novo
    ("05_batch_process", "Processamento em Lote", ["GDRIVE_TEST_FOLDER"])  # Novo
]
```

### **Validações Customizadas**
Adicione validações específicas por teste na função `_run_example_test()`:

```python
elif test_id == "04_recursive":
    if "NAVEGAÇÃO RECURSIVA CONCLUÍDA" in result.stdout:
        print("   ✅ Navegação recursiva validada")
    else:
        print("   ⚠️  Navegação recursiva pode ter falhado")
```

## 📊 **Integração com Desenvolvimento**

### **Pre-commit Hook**
```bash
# .git/hooks/pre-commit
#!/bin/bash
echo "Validando examples antes do commit..."
python scripts/validate_examples.py --skip-auth
if [ $? -ne 0 ]; then
    echo "❌ Examples falharam na validação. Corrija antes de commitar."
    exit 1
fi
```

### **Makefile Integration**
```makefile
.PHONY: validate
validate:
	python scripts/validate_examples.py

.PHONY: validate-quick
validate-quick:
	python scripts/validate_examples.py --skip-auth

.PHONY: validate-full
validate-full:
	python scripts/validate_examples.py --save-report full_report.txt
```

## 🚀 **Futuras Expansões**

### **Scripts Planejados:**
- **`benchmark_examples.py`** - Performance benchmarking
- **`generate_docs.py`** - Geração automática de documentação
- **`setup_dev_env.py`** - Setup automático do ambiente de dev
- **`migrate_config.py`** - Migração de configurações antigas

### **Melhorias no Validador:**
- Validação de performance (tempo máximo por teste)
- Validação de saída estruturada (JSON, XML)
- Testes de stress (muitos arquivos)
- Validação de diferentes tipos MIME
- Integração com pytest para testes unitários

## 💡 **Dicas de Uso**

### **Para Desenvolvimento:**
```bash
# Ciclo rápido de desenvolvimento
python scripts/validate_examples.py --skip-auth --folder-id PASTA_DEV
```

### **Para Documentação:**
```bash
# Gera evidências para documentação
python scripts/validate_examples.py --save-report docs/validation_evidence.txt
```

### **Para Debugging:**
```bash
# Se validador falhar, execute manualmente:
cd SmartSearchHUB
export GDRIVE_TEST_FOLDER="folder_id"
python -m examples.gdrive 03
```

---

**🛠️ Scripts que facilitam o desenvolvimento e garantem qualidade dos Examples!**