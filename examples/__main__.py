# examples/__main__.py
"""
Entrypoint principal para examples do SmartSearchHUB.

Coordena execução de examples de diferentes provedores e funcionalidades.
Compatível com execução via PowerShell no Windows.

Uso:
    python -m examples                     # Menu interativo
    python -m examples --list              # Lista todos os examples
    python -m examples gdrive              # Executa examples do gdrive
    python -m examples gdrive --list       # Lista examples do gdrive
    python -m examples gdrive 01           # Executa example específico
    python -m examples --setup             # Setup inicial completo

Compatibilidade:
    ✅ python -m examples.gdrive            # Acesso direto ao submódulo
    ✅ python -m examples.gdrive.01_auth_test  # Example específico
"""

import sys
import os
import argparse
import importlib
from pathlib import Path
from typing import Dict, List, Optional

# Garante que o projeto está no path
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


class ExamplesCoordinator:
    """Coordenador principal de todos os examples."""

    def __init__(self):
        self.examples_dir = Path(__file__).parent

        # Mapeia provedores/módulos disponíveis
        self.providers = {
            "gdrive": {
                "title": "Google Drive",
                "description": "Examples para integração com Google Drive",
                "module": "examples.gdrive",
                "implemented": True
            },
            "url": {
                "title": "URLs",
                "description": "Examples para busca em URLs e sites",
                "module": "examples.url",
                "implemented": False
            },
            "common": {
                "title": "Utilitários Comuns",
                "description": "Testes dos utilitários compartilhados",
                "module": "examples.common",
                "implemented": False
            }
        }

    def show_welcome(self):
        """Mostra mensagem de boas-vindas."""
        print("🔍 SMARTSEARCHHUB - EXAMPLES")
        print("=" * 50)
        print("Framework modular de busca e indexação de arquivos")
        print()

    def list_all_providers(self):
        """Lista todos os provedores disponíveis."""
        print("📋 Provedores disponíveis:")
        print("-" * 40)

        for key, info in self.providers.items():
            status = "✅" if info.get("implemented", True) else "🚧"
            print(f"{status} {key:<10} {info['title']}")
            print(f"   {info['description']}")
            print()

        print("Uso:")
        print("  python -m examples gdrive           # Examples do Google Drive")
        print("  python -m examples gdrive --list    # Lista examples do gdrive")
        print("  python -m examples --setup          # Setup inicial")

    def run_provider(self, provider: str, args: List[str]) -> int:
        """Executa examples de um provedor específico."""
        if provider not in self.providers:
            print(f"❌ Provedor '{provider}' não encontrado")
            self.list_all_providers()
            return 1

        provider_info = self.providers[provider]

        if not provider_info.get("implemented", True):
            print(f"🚧 Provedor '{provider}' ainda não implementado")
            return 2

        try:
            # Importa o módulo do provedor
            module_name = provider_info["module"]
            spec = importlib.util.find_spec(f"{module_name}.__main__")

            if spec is None:
                print(f"❌ Módulo {module_name}.__main__ não encontrado")
                return 3

            # Executa o __main__ do provedor com argumentos
            module = importlib.import_module(f"{module_name}.__main__")

            # Simula sys.argv para o submódulo
            original_argv = sys.argv.copy()
            try:
                sys.argv = [f"python -m {module_name}"] + args
                if hasattr(module, 'main'):
                    return module.main()
                else:
                    print(f"❌ Módulo {module_name} não tem função main()")
                    return 4
            finally:
                sys.argv = original_argv

        except ImportError as e:
            print(f"❌ Erro ao importar {module_name}: {e}")
            return 5
        except Exception as e:
            print(f"❌ Erro ao executar {provider}: {e}")
            if os.getenv("DEBUG"):
                import traceback
                traceback.print_exc()
            return 6

    def setup_all(self) -> int:
        """Setup inicial completo."""
        print("🔧 SETUP INICIAL COMPLETO")
        print("=" * 40)

        success_count = 0

        # Setup do Google Drive
        try:
            print("\n📁 Configurando Google Drive...")
            from examples.common.auth_manager import AuthManager

            auth = AuthManager()
            auth.create_example_configs()
            success_count += 1

        except Exception as e:
            print(f"❌ Erro no setup do Google Drive: {e}")

        # Future: Setup para outros provedores

        print(f"\n📊 Setup concluído: {success_count} provedor(es) configurado(s)")

        if success_count > 0:
            print("\n💡 Próximos passos:")
            print("1. Configure suas credenciais nos arquivos criados")
            print("2. Execute: python -m examples gdrive 01")
            print("3. Explore outros examples: python -m examples gdrive --list")
            return 0
        else:
            print("❌ Nenhum setup foi bem-sucedido")
            return 1

    def interactive_menu(self) -> int:
        """Menu interativo para escolha de examples."""
        self.show_welcome()

        while True:
            print("\n🎯 O que você quer fazer?")
            print("1. Ver provedores disponíveis")
            print("2. Executar examples do Google Drive")
            print("3. Setup inicial (configurações)")
            print("4. Sair")

            try:
                choice = input("\nEscolha uma opção (1-4): ").strip()

                if choice == "1":
                    print()
                    self.list_all_providers()

                elif choice == "2":
                    print()
                    return self.run_provider("gdrive", [])

                elif choice == "3":
                    print()
                    return self.setup_all()

                elif choice == "4":
                    print("👋 Até logo!")
                    return 0

                else:
                    print("❌ Opção inválida. Escolha 1, 2, 3 ou 4.")

            except (KeyboardInterrupt, EOFError):
                print("\n👋 Até logo!")
                return 0


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Coordenador de examples do SmartSearchHUB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python -m examples                          # Menu interativo
  python -m examples --list                   # Lista provedores
  python -m examples --setup                  # Setup inicial
  python -m examples gdrive                   # Examples do Google Drive
  python -m examples gdrive --list            # Lista examples do gdrive
  python -m examples gdrive 01                # Example específico

Acesso direto (alternativo):
  python -m examples.gdrive                   # Equivale ao acima
  python -m examples.gdrive.01_auth_test      # Example específico
        """
    )

    parser.add_argument(
        "provider",
        nargs="?",
        help="Provedor específico (gdrive, url, etc.)"
    )

    parser.add_argument(
        "provider_args",
        nargs="*",
        help="Argumentos para o provedor"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="Lista todos os provedores disponíveis"
    )

    parser.add_argument(
        "--setup",
        action="store_true",
        help="Setup inicial completo"
    )

    args = parser.parse_args()

    coordinator = ExamplesCoordinator()

    # Processamento de argumentos
    if args.setup:
        return coordinator.setup_all()

    if args.list:
        coordinator.show_welcome()
        coordinator.list_all_providers()
        return 0

    if args.provider:
        return coordinator.run_provider(args.provider, args.provider_args)

    # Sem argumentos - menu interativo
    return coordinator.interactive_menu()


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n⏹️  Execução interrompida pelo usuário")
        exit(130)
    except Exception as e:
        print(f"\n💥 Erro inesperado no coordenador: {e}")
        if os.getenv("DEBUG"):
            import traceback

            traceback.print_exc()
        exit(1)