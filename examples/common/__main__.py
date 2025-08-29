# examples/common/__main__.py
"""
Helper para testar e configurar o AuthManager diretamente.

Uso:
    python -m examples.common                   # Teste rápido
    python -m examples.common create-examples  # Cria arquivos de exemplo
    python -m examples.common test-detection   # Testa detecção de configs
"""

import sys
import os
from pathlib import Path

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

try:
    from .auth_manager import AuthManager
except ImportError:
    from auth_manager import AuthManager


def test_detection():
    """Testa detecção de configurações."""
    print("🔍 TESTE DE DETECÇÃO DE CONFIGURAÇÕES")
    print("=" * 50)

    auth = AuthManager(interactive=False)

    print(f"📁 Diretório de config: {auth.config_dir}")
    print(f"📄 Arquivo de auth: {auth.gdrive_auth_file}")
    print(f"🗂️  Diretório de credenciais: {auth.credentials_dir}")

    # Verifica se diretórios existem
    print(f"\n📋 Status dos diretórios:")
    print(f"  config/: {'✅ Existe' if auth.config_dir.exists() else '❌ Não existe'}")
    print(f"  credentials/: {'✅ Existe' if auth.credentials_dir.exists() else '❌ Não existe'}")

    # Testa detecção
    print(f"\n🔍 Detectando configurações...")
    try:
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
            print("⚠️  Nenhuma configuração detectada")

    except Exception as e:
        print(f"❌ Erro na detecção: {e}")

    # Lista arquivos na pasta credentials
    print(f"\n📁 Arquivos em credentials/:")
    if auth.credentials_dir.exists():
        json_files = list(auth.credentials_dir.glob("*.json"))
        if json_files:
            for file in json_files:
                print(f"  📄 {file.name}")
        else:
            print("  (nenhum arquivo .json encontrado)")
    else:
        print("  (diretório não existe)")

    # Variáveis de ambiente relevantes
    print(f"\n🌍 Variáveis de ambiente:")
    env_vars = ["GOOGLE_APPLICATION_CREDENTIALS", "GDRIVE_INTERACTIVE", "DEBUG"]
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if "CREDENTIALS" in var:
                value = f".../{Path(value).name}" if Path(value).exists() else value
            print(f"  {var}={value}")
        else:
            print(f"  {var}=(não definida)")


def create_examples():
    """Cria arquivos de exemplo."""
    print("📝 CRIANDO ARQUIVOS DE EXEMPLO")
    print("=" * 40)

    try:
        auth = AuthManager()
        auth.create_example_configs()
        print("\n✅ Arquivos de exemplo criados com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao criar exemplos: {e}")
        return 1

    return 0


def quick_test():
    """Teste rápido geral."""
    print("🧪 TESTE RÁPIDO DO AUTHMANAGER")
    print("=" * 40)

    try:
        # Teste não-interativo
        auth = AuthManager(interactive=False, save_tokens=True)

        print(f"✅ AuthManager inicializado")
        print(f"   Interactive: {auth.interactive}")
        print(f"   Save tokens: {auth.save_tokens}")
        print(f"   Config dir: {auth.config_dir}")

        # Teste de detecção
        config_data = auth._load_gdrive_config()
        print(f"✅ Detecção executada: {len(config_data)} configuração(ões) encontrada(s)")

        if config_data:
            print("   Chaves encontradas:", list(config_data.keys()))
        else:
            print("   💡 Execute 'create-examples' para criar templates")

    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        if os.getenv("DEBUG"):
            import traceback
            traceback.print_exc()
        return 1

    return 0


def main():
    """Função principal."""
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "create-examples":
            return create_examples()
        elif command == "test-detection":
            return test_detection()
        elif command == "quick-test":
            return quick_test()
        else:
            print(f"❌ Comando desconhecido: {command}")
            print("💡 Comandos disponíveis: create-examples, test-detection, quick-test")
            return 1
    else:
        # Sem argumentos - executa teste rápido
        return quick_test()


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n⏹️  Teste interrompido")
        exit(130)