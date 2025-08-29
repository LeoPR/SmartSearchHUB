# examples/gdrive/__main__.py
"""
Coordenador de examples para Google Drive.

Executa todos os examples do gdrive em sequência ou permite escolher específicos.

Uso:
    python -m examples.gdrive              # Executa todos em sequência
    python -m examples.gdrive --list       # Lista examples disponíveis  
    python -m examples.gdrive 01           # Executa apenas o 01_auth_test
    python -m examples.gdrive 01 02        # Executa 01 e 02
    python -m examples.gdrive --setup      # Setup inicial (criar configs)

Variáveis de ambiente:
    GDRIVE_TEST_FOLDER=folder_id           # Pasta para testes (necessário para 02+)
    GDRIVE_INTERACTIVE=false               # Força modo não-interativo
    GDRIVE_STOP_ON_ERROR=true              # Para na primeira falha
"""

import sys
import os
import argparse
import importlib
from pathlib import Path
from typing import List, Dict, Tuple

# Garante importação correta
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


class GDriveExamplesRunner:
    """Coordenador para executar examples do Google Drive."""

    def __init__(self):
        self.examples_dir = Path(__file__).parent
        self.stop_on_error = os.getenv("GDRIVE_STOP_ON_ERROR", "true").lower() == "true"

        # Mapeamento de examples disponíveis
        self.available_examples = {
            "01": {
                "name": "01_auth_test",
                "title": "Teste de Autenticação",
                "description": "Verifica se a autenticação com Google Drive está funcionando",
                "requires": [],
                "module": "examples.gdrive.01_auth_test"
            },
            "02": {
                "name": "02_list_basic",
                "title": "Listagem Básica",
                "description": "Lista arquivos de uma pasta sem fazer downloads",
                "requires": ["GDRIVE_TEST_FOLDER"],
                "module": "examples.gdrive.02_list_basic"
            },
            # Placeholder para futuros examples
            "03": {
                "name": "03_extract_html",
                "title": "Extração de HTML/Texto",
                "description": "Extrai conteúdo de arquivos HTML e texto",
                "requires": ["GDRIVE_TEST_FOLDER"],
                "module": "examples.gdrive.03_extract_html",
                "implemented": False
            }
        }

    def list_examples(self) -> None:
        """Lista examples disponíveis."""
        print("📋 Examples disponíveis para Google Drive:")
        print("=" * 70)

        for key, info in self.available_examples.items():
            status = "✅" if info.get("implemented", True) else "🚧"
            print(f"{status} {key}: {info['title']}")
            print(f"   {info['description']}")

            if info.get("requires"):
                requires_str = ", ".join(info["requires"])
                print(f"   Requer: {requires_str}")

            print()

        print("Uso:")
        print("  python -m examples.gdrive           # Executa todos")
        print("  python -m examples.gdrive 01        # Executa apenas 01")
        print("  python -m examples.gdrive 01 02     # Executa 01 e 02")

    def check_requirements(self, example_key: str) -> Tuple[bool, List[str]]:
        """Verifica se os requisitos para um example estão satisfeitos."""
        example = self.available_examples.get(example_key, {})
        requires = example.get("requires", [])
        missing = []

        for req in requires:
            if not os.getenv(req):
                missing.append(req)

        return len(missing) == 0, missing

    def run_example(self, example_key: str) -> int:
        """Executa um example específico."""
        if example_key not in self.available_examples:
            print(f"❌ Example '{example_key}' não encontrado")
            return 1

        example = self.available_examples[example_key]

        # Verifica se está implementado
        if not example.get("implemented", True):
            print(f"🚧 Example '{example_key}' ainda não implementado")
            return 2

        # Verifica requisitos
        satisfied, missing = self.check_requirements(example_key)
        if not satisfied:
            print(f"❌ Example '{example_key}' requer variáveis de ambiente:")
            for req in missing:
                print(f"   {req}=<valor>")
            print(f"💡 Exemplo: {missing[0]}=1AbCdEf python -m examples.gdrive {example_key}")
            return 3

        print(f"🚀 Executando: {example['title']}")
        print("-" * 50)

        try:
            # Importa e executa o módulo
            module = importlib.import_module(example["module"])
            if hasattr(module, 'main'):
                result = module.main()
                return result if result is not None else 0
            else:
                print(f"❌ Módulo {example['module']} não tem função main()")
                return 4

        except ImportError as e:
            print(f"❌ Erro ao importar {example['module']}: {e}")
            return 5
        except Exception as e:
            print(f"❌ Erro ao executar {example['name']}: {e}")
            return 6

    def run_multiple(self, example_keys: List[str]) -> int:
        """Executa múltiplos examples em sequência."""
        total_examples = len(example_keys)
        successful = 0
        failed = []

        print(f"🎯 Executando {total_examples} example(s) em sequência")
        print("=" * 60)

        for i, example_key in enumerate(example_keys, 1):
            print(f"\n[{i}/{total_examples}] Example {example_key}")

            result = self.run_example(example_key)

            if result == 0:
                print(f"✅ Example {example_key} executado com sucesso")
                successful += 1
            else:
                print(f"❌ Example {example_key} falhou (código {result})")
                failed.append((example_key, result))

                if self.stop_on_error:
                    print(f"⏹️  Parando execução (GDRIVE_STOP_ON_ERROR=true)")
                    break

            # Separador entre examples
            if i < total_examples:
                print("\n" + "─" * 60)

        # Resumo final
        print("\n" + "=" * 60)
        print("📊 RESUMO DA EXECUÇÃO")
        print(f"✅ Sucessos: {successful}/{total_examples}")

        if failed:
            print(f"❌ Falhas: {len(failed)}")
            for example_key, code in failed:
                example_title = self.available_examples[example_key]["title"]
                print(f"   {example_key} ({example_title}): código {code}")

        return 0 if len(failed) == 0 else 1

    def setup_initial_config(self) -> int:
        """Setup inicial - cria arquivos de configuração."""
        print("🔧 SETUP INICIAL - GOOGLE DRIVE")
        print("=" * 50)

        try:
            from examples.common.auth_manager import AuthManager

            auth = AuthManager()
            auth.create_example_configs()

            print("\n💡 Próximos passos:")
            print("1. Baixe credenciais do Google Console (OAuth ou Service Account)")
            print("2. Salve em ./config/credentials/")
            print("3. Ajuste ./config/gdrive_auth.json conforme necessário")
            print("4. Execute: python -m examples.gdrive 01")

            return 0

        except Exception as e:
            print(f"❌ Erro no setup: {e}")
            return 1

    def get_implemented_examples(self) -> List[str]:
        """Retorna lista de examples implementados."""
        return [
            key for key, info in self.available_examples.items()
            if info.get("implemented", True)
        ]


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Coordenador de examples para Google Drive",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python -m examples.gdrive                    # Executa todos
  python -m examples.gdrive --list             # Lista disponíveis
  python -m examples.gdrive --setup            # Setup inicial
  python -m examples.gdrive 01                 # Executa apenas 01
  python -m examples.gdrive 01 02              # Executa 01 e 02

Variáveis de ambiente úteis:
  GDRIVE_TEST_FOLDER=1AbCdEf                   # Pasta para testes
  GDRIVE_INTERACTIVE=false                     # Modo não-interativo
  GDRIVE_STOP_ON_ERROR=false                   # Continua mesmo com erros
        """
    )

    parser.add_argument(
        "examples",
        nargs="*",
        help="Examples específicos para executar (01, 02, etc.)"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="Lista examples disponíveis"
    )

    parser.add_argument(
        "--setup",
        action="store_true",
        help="Setup inicial (criar arquivos de configuração)"
    )

    args = parser.parse_args()

    runner = GDriveExamplesRunner()

    # Processamento de argumentos
    if args.setup:
        return runner.setup_initial_config()

    if args.list:
        runner.list_examples()
        return 0

    # Determina quais examples executar
    if args.examples:
        # Examples específicos fornecidos
        example_keys = []
        for ex in args.examples:
            if ex in runner.available_examples:
                example_keys.append(ex)
            else:
                print(f"❌ Example '{ex}' não encontrado")
                print("💡 Use --list para ver examples disponíveis")
                return 1
    else:
        # Executa todos os implementados
        example_keys = runner.get_implemented_examples()
        if not example_keys:
            print("❌ Nenhum example implementado encontrado")
            return 1

    # Executa examples
    if len(example_keys) == 1:
        return runner.run_example(example_keys[0])
    else:
        return runner.run_multiple(example_keys)


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n⏹️  Execução interrompida pelo usuário")
        exit(130)
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        if os.getenv("DEBUG"):
            import traceback

            traceback.print_exc()
        exit(1)