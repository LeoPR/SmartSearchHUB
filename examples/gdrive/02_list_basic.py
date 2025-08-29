# examples/gdrive/02_list_basic.py
"""
Lista conteúdo básico de uma pasta do Google Drive.

Mostra apenas informações básicas dos arquivos sem fazer downloads.
Útil para verificar conectividade e explorar estrutura de pastas.

Uso:
    GDRIVE_TEST_FOLDER=1AbCdEf python -m examples.gdrive.02_list_basic

Variáveis de ambiente:
    GDRIVE_TEST_FOLDER=folder_id     # ID da pasta (obrigatório)
    GDRIVE_MAX_FILES=10              # Máximo de arquivos a listar (default: 10)
"""

import os
import sys
from pathlib import Path

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

try:
    from examples.common.auth_manager import AuthManager
    from src.api.facade import Folder
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)


def main():
    """Lista conteúdo básico da pasta."""
    print("=" * 60)
    print("📁 LISTAGEM BÁSICA - GOOGLE DRIVE")
    print("=" * 60)

    # Verifica ID da pasta
    folder_id = os.getenv("GDRIVE_TEST_FOLDER")
    if not folder_id:
        print("❌ Defina GDRIVE_TEST_FOLDER com o ID da pasta")
        print("💡 Exemplo: GDRIVE_TEST_FOLDER=1AbCdEf python -m examples.gdrive.02_list_basic")
        return 1

    max_files = int(os.getenv("GDRIVE_MAX_FILES", "10"))

    print(f"📂 Pasta: {folder_id}")
    print(f"📊 Máximo de arquivos: {max_files}")

    try:
        # Autenticação
        print("\n🔐 Autenticando...")
        auth = AuthManager(interactive=True, save_tokens=True)
        config = auth.get_gdrive_config()

        # Conectar à pasta
        print(f"\n🔗 Conectando à pasta...")
        folder_uri = f"gdrive://{folder_id}"
        folder = Folder.from_uri(
            folder_uri,
            config=config,
            tmp="./tmp",
            cache="./cache"
        )

        # Informações da pasta
        print("\n📋 Informações da pasta:")
        info = folder.info()
        for key, value in info.items():
            print(f"  {key}: {value}")

        # Listar arquivos
        print(f"\n📄 Listando arquivos...")
        objects = folder.list()

        total_count = len(objects)
        display_count = min(max_files, total_count)

        print(f"\n📊 Encontrados {total_count} arquivo(s), exibindo primeiros {display_count}:")
        print("-" * 80)
        print(f"{'Nome':<40} {'Tipo MIME':<30} {'ID':<15}")
        print("-" * 80)

        for i, obj in enumerate(objects[:display_count]):
            # Trunca nome se muito longo
            name = obj.name
            if len(name) > 37:
                name = name[:34] + "..."

            # Trunca MIME type se muito longo
            mime = obj.mimetype or "desconhecido"
            if len(mime) > 27:
                mime = mime[:24] + "..."

            # ID truncado para exibição
            obj_id = getattr(obj, 'id', 'N/A')
            if len(obj_id) > 12:
                obj_id = obj_id[:12] + "..."

            print(f"{name:<40} {mime:<30} {obj_id:<15}")

        if total_count > display_count:
            print("-" * 80)
            print(f"... e mais {total_count - display_count} arquivo(s)")
            print(f"💡 Use GDRIVE_MAX_FILES={total_count} para ver todos")

        # Estatísticas por tipo
        print(f"\n📈 Estatísticas por tipo MIME:")
        mime_stats = {}
        for obj in objects:
            mime = obj.mimetype or "desconhecido"
            mime_stats[mime] = mime_stats.get(mime, 0) + 1

        for mime_type, count in sorted(mime_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {mime_type}: {count} arquivo(s)")

        print("\n" + "=" * 60)
        print("🎉 LISTAGEM CONCLUÍDA COM SUCESSO!")
        print("💡 Use examples.gdrive.03_extract_html para extrair conteúdo")
        print("=" * 60)

        return 0

    except KeyboardInterrupt:
        print("\n⏹️  Operação interrompida pelo usuário.")
        return 130

    except Exception as e:
        print(f"\n❌ Erro: {e}")

        if os.getenv("DEBUG"):
            import traceback
            traceback.print_exc()

        return 1


if __name__ == "__main__":
    exit(main())