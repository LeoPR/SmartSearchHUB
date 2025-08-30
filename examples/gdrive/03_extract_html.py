# examples/gdrive/03_extract_html.py
"""
Extração avançada de conteúdo HTML e texto do Google Drive.

Funcionalidades:
- Filtra automaticamente arquivos de texto/HTML
- Extrai dados brutos + texto limpo
- Analisa links (internos vs externos)
- Mostra estatísticas detalhadas
- Configurável via variáveis de ambiente

Uso:
    GDRIVE_TEST_FOLDER=1AbCdEf python -m examples.gdrive.03_extract_html

Variáveis de ambiente:
    GDRIVE_TEST_FOLDER=folder_id           # ID da pasta (obrigatório)
    GDRIVE_MAX_FILES=5                     # Máximo de arquivos a processar (default: 5)
    GDRIVE_PREVIEW_LENGTH=300              # Tamanho do preview (default: 300)
    GDRIVE_EXTRACT_LINKS=true              # Extrair links (default: true)
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
    from examples.common.content_extractor import ContentExtractor
    from src.api.facade import Folder
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)


def main():
    """Extração avançada de conteúdo HTML/texto."""
    print("=" * 70)
    print("📄 EXTRAÇÃO DE CONTEÚDO HTML/TEXTO - GOOGLE DRIVE")
    print("=" * 70)

    # Configuração a partir de variáveis de ambiente
    folder_id = os.getenv("GDRIVE_TEST_FOLDER")
    if not folder_id:
        print("❌ Defina GDRIVE_TEST_FOLDER com o ID da pasta")
        print("💡 Exemplo: GDRIVE_TEST_FOLDER=1AbCdEf python -m examples.gdrive.03_extract_html")
        return 1

    max_files = int(os.getenv("GDRIVE_MAX_FILES", "5"))
    preview_length = int(os.getenv("GDRIVE_PREVIEW_LENGTH", "300"))
    extract_links = os.getenv("GDRIVE_EXTRACT_LINKS", "true").lower() == "true"

    print(f"📂 Pasta: {folder_id}")
    print(f"📊 Máximo de arquivos: {max_files}")
    print(f"📏 Tamanho do preview: {preview_length} caracteres")
    print(f"🔗 Extrair links: {'✅ Sim' if extract_links else '❌ Não'}")

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

        # Listar arquivos
        print(f"\n📋 Listando arquivos...")
        all_objects = folder.list()

        # Configurar extrator
        extractor = ContentExtractor(
            extract_links=extract_links,
            preview_length=preview_length
        )

        # Filtrar arquivos processáveis
        extractable_files = extractor.filter_extractable_files(all_objects)

        if not extractable_files:
            print("⚠️  Nenhum arquivo de texto/HTML encontrado na pasta.")
            print("💡 O exemplo procura por arquivos HTML, Google Docs e texto.")
            return 0

        # Limitar quantidade
        files_to_process = extractable_files[:max_files]

        print(f"\n📊 Arquivos encontrados:")
        print(f"   Total na pasta: {len(all_objects)}")
        print(f"   Arquivos de texto/HTML: {len(extractable_files)}")
        print(f"   A processar: {len(files_to_process)}")

        # Processamento
        print(f"\n🚀 Processando arquivos...")
        print("=" * 70)

        total_words = 0
        total_links = 0
        processed_count = 0

        for i, file_obj in enumerate(files_to_process, 1):
            print(f"\n[{i}/{len(files_to_process)}] 📄 {file_obj.name}")
            print(f"   Tipo: {file_obj.mimetype}")

            try:
                # Extração
                result = extractor.extract_content(
                    file_obj,
                    head={"characters": preview_length * 3}  # Lê mais do que o preview
                )

                if result.get('error'):
                    print(f"   ❌ Erro: {result['error']}")
                    continue

                # Estatísticas
                stats = result['statistics']
                links = result['links']
                metadata = result['metadata']

                print(f"   📊 Estatísticas:")
                print(f"      Tipo detectado: {metadata['content_type']}")
                print(f"      Tamanho bruto: {stats['raw_length']:,} caracteres")
                print(f"      Texto limpo: {stats['clean_length']:,} caracteres")
                print(f"      Linhas: {stats['clean_lines']}")
                print(f"      Palavras: {stats['word_count']:,}")
                
                if stats['compression_ratio'] > 0:
                    print(f"      Taxa de compressão: {stats['compression_ratio']:.1%}")

                # Links
                if extract_links and links:
                    external_links = [l for l in links if l.get('is_external', False)]
                    internal_links = [l for l in links if l.get('is_internal', False)]
                    anchors = [l for l in links if l.get('is_anchor', False)]

                    print(f"   🔗 Links encontrados: {len(links)} total")
                    if external_links:
                        print(f"      Externos: {len(external_links)}")
                    if internal_links:
                        print(f"      Internos: {len(internal_links)}")
                    if anchors:
                        print(f"      Âncoras: {len(anchors)}")

                    # Mostra alguns links externos
                    if external_links:
                        print(f"      Exemplos externos:")
                        for link in external_links[:3]:
                            link_text = link['text'][:40] + "..." if len(link['text']) > 40 else link['text']
                            print(f"        • {link_text} → {link['url']}")

                # Preview do conteúdo
                if result['clean_text']:
                    preview = result['preview']
                    print(f"   📝 Preview:")
                    # Quebra preview em linhas para melhor visualização
                    lines = preview.split('\n')
                    for line in lines[:3]:  # Primeiras 3 linhas
                        if line.strip():
                            line_preview = line[:80] + "..." if len(line) > 80 else line
                            print(f"      {line_preview}")

                # Acumuladores
                total_words += stats['word_count']
                total_links += len(links)
                processed_count += 1

            except Exception as e:
                print(f"   ❌ Erro no processamento: {e}")
                if os.getenv("DEBUG"):
                    import traceback
                    traceback.print_exc()

        # Resumo final
        print("\n" + "=" * 70)
        print("📊 RESUMO FINAL")
        print("=" * 70)
        print(f"✅ Arquivos processados: {processed_count}/{len(files_to_process)}")
        print(f"📝 Total de palavras: {total_words:,}")
        
        if extract_links:
            print(f"🔗 Total de links: {total_links}")

        if processed_count > 0:
            avg_words = total_words / processed_count
            print(f"📊 Média de palavras por arquivo: {avg_words:.0f}")

        print("\n💡 Para processar mais arquivos:")
        print(f"   GDRIVE_MAX_FILES={len(extractable_files)} python -m examples.gdrive.03_extract_html")
        
        print("\n💡 Para ver links detalhados:")
        print(f"   GDRIVE_EXTRACT_LINKS=true python -m examples.gdrive.03_extract_html")

        print("\n🎉 EXTRAÇÃO CONCLUÍDA COM SUCESSO!")

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