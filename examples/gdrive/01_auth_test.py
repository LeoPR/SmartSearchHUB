# examples/gdrive/01_auth_test.py
"""
Teste básico de autenticação Google Drive.

Verifica se consegue autenticar e obter credenciais válidas.
Não lista arquivos nem faz downloads, apenas testa a autenticação.

Uso:
    python -m examples.gdrive.01_auth_test

Variáveis de ambiente opcionais:
    GDRIVE_INTERACTIVE=false  # Força modo não-interativo
    GOOGLE_APPLICATION_CREDENTIALS=path  # Service account
"""

import os
import sys
from pathlib import Path

# Garante que consegue importar o módulo
if __name__ == "__main__":
    # Adiciona path do projeto se executado diretamente
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

try:
    from examples.common.auth_manager import AuthManager
except ImportError as e:
    print(f"❌ Erro ao importar AuthManager: {e}")
    print("💡 Execute a partir da raiz do projeto: python -m examples.gdrive.01_auth_test")
    sys.exit(1)


def main():
    """Teste principal de autenticação."""
    print("=" * 60)
    print("🔐 TESTE DE AUTENTICAÇÃO GOOGLE DRIVE")
    print("=" * 60)

    # Configuração baseada em variáveis de ambiente
    interactive = os.getenv("GDRIVE_INTERACTIVE", "true").lower() != "false"

    print(f"Modo interativo: {'✅ Sim' if interactive else '❌ Não'}")
    print(f"Diretório de trabalho: {Path.cwd()}")

    try:
        # Inicializa AuthManager
        print("\n🚀 Inicializando AuthManager...")
        auth = AuthManager(interactive=interactive, save_tokens=True)
        print(f"📁 Diretório de config: {auth.config_dir}")
        print(f"📄 Arquivo de auth: {auth.gdrive_auth_file}")

        # Verifica se diretórios existem
        if not auth.config_dir.exists():
            print(f"⚠️  Diretório de config não existe: {auth.config_dir}")
            print("💡 Será criado automaticamente...")

        # Testa detecção de configurações
        print("\n🔍 Detectando configurações existentes...")
        config_data = auth._load_gdrive_config()

        if config_data:
            print("✅ Configurações encontradas:")
            for key, value in config_data.items():
                if key == "credentials_file" and value:
                    # Mostra apenas nome do arquivo por segurança
                    print(f"  {key}: .../{Path(value).name}")
                else:
                    print(f"  {key}: {value}")
        else:
            print("⚠️  Nenhuma configuração detectada.")
            print("\n💡 Para configurar autenticação:")
            print("1. Execute: python -m examples.common.auth_manager create-examples")
            print("2. Configure seus arquivos de credenciais")
            print("3. Execute este teste novamente")
            return 1

        # Tenta obter configuração válida
        print("\n🔐 Testando autenticação...")
        config = auth.get_gdrive_config()

        print(f"✅ Autenticação bem-sucedida!")
        print(f"   Método: {config.auth_method}")
        print(f"   Scopes: {len(config.scopes)} configurado(s)")

        # Teste adicional: verificar se credenciais são válidas
        print("\n🧪 Verificando credenciais...")
        try:
            creds = config.build_credentials()
            if hasattr(creds, 'valid') and creds.valid:
                print("✅ Credenciais válidas e prontas para uso!")
            elif hasattr(creds, 'token'):
                print("✅ Credenciais obtidas com sucesso!")
            else:
                print("✅ Credenciais criadas (tipo service account)!")

        except Exception as e:
            print(f"❌ Erro ao verificar credenciais: {e}")
            return 1

        print("\n" + "=" * 60)
        print("🎉 TESTE DE AUTENTICAÇÃO CONCLUÍDO COM SUCESSO!")
        print("💡 Agora você pode executar outros examples do gdrive")
        print("=" * 60)

        return 0

    except KeyboardInterrupt:
        print("\n⏹️  Teste interrompido pelo usuário.")
        return 130

    except FileNotFoundError as e:
        print(f"\n❌ Arquivo não encontrado: {e}")
        print("\n💡 Soluções possíveis:")
        print("1. Configure GOOGLE_APPLICATION_CREDENTIALS para service account")
        print("2. Crie arquivo ./config/gdrive_auth.json com suas credenciais")
        print("3. Execute com interactive=True para setup automático")
        return 2

    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        print(f"Tipo: {type(e).__name__}")

        # Debug info em caso de erro
        if os.getenv("DEBUG"):
            import traceback
            print("\n🐛 Stack trace completo:")
            traceback.print_exc()
        else:
            print("💡 Execute com DEBUG=1 para mais informações")

        return 1


if __name__ == "__main__":
    exit(main())